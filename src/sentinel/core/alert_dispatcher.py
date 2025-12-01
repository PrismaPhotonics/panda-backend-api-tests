"""
Alert Dispatcher
================

Delivers alerts to configured channels (Slack, email, webhooks).
"""

import logging
import json
from datetime import datetime
from typing import Dict, List, Optional, Callable
from dataclasses import asdict

import requests
from requests.exceptions import RequestException

from src.sentinel.core.models import Anomaly, AnomalySeverity, RunContext


class AlertDispatcher:
    """
    Dispatches alerts to configured channels.
    
    Supports:
    - Slack webhooks
    - Email (SMTP)
    - Generic webhooks
    - Multiple channels with severity filtering
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize alert dispatcher.
        
        Args:
            config: Configuration dictionary with alert channel settings
        """
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Load alert channels from config
        self.channels = self._load_channels()
        
        # Alert history (to prevent spam)
        self._recent_alerts: Dict[str, datetime] = {}
        self._alert_cooldown_seconds = self.config.get("alert_cooldown_seconds", 300)
    
    def _load_channels(self) -> List[Dict]:
        """Load alert channels from configuration."""
        channels = []
        
        config_channels = self.config.get("channels", [])
        for channel_config in config_channels:
            channel = {
                "type": channel_config.get("type"),  # slack, email, webhook
                "webhook_url": channel_config.get("webhook_url"),
                "email_to": channel_config.get("to", []),
                "severity_min": AnomalySeverity(channel_config.get("severity_min", "warning")),
                "enabled": channel_config.get("enabled", True)
            }
            channels.append(channel)
        
        return channels
    
    def dispatch_anomaly(self, anomaly: Anomaly, context: RunContext):
        """
        Dispatch an anomaly alert to appropriate channels.
        
        Args:
            anomaly: Anomaly to alert about
            context: RunContext
        """
        # Check cooldown
        alert_key = f"{anomaly.anomaly_id}:{anomaly.severity.value}"
        if self._is_in_cooldown(alert_key):
            self.logger.debug(f"Alert {alert_key} is in cooldown, skipping")
            return
        
        # Mark as alerted
        anomaly.alerted = True
        anomaly.alert_timestamp = datetime.now()
        self._recent_alerts[alert_key] = datetime.now()
        
        # Dispatch to each channel
        for channel in self.channels:
            if not channel.get("enabled", True):
                continue
            
            # Check severity threshold
            if not self._meets_severity_threshold(anomaly.severity, channel["severity_min"]):
                continue
            
            try:
                if channel["type"] == "slack":
                    self._send_slack_alert(anomaly, context, channel)
                elif channel["type"] == "email":
                    self._send_email_alert(anomaly, context, channel)
                elif channel["type"] == "webhook":
                    self._send_webhook_alert(anomaly, context, channel)
            except Exception as e:
                self.logger.error(f"Error sending alert to {channel['type']}: {e}", exc_info=True)
    
    def _meets_severity_threshold(
        self,
        severity: AnomalySeverity,
        min_severity: AnomalySeverity
    ) -> bool:
        """Check if severity meets channel threshold."""
        severity_order = {
            AnomalySeverity.INFO: 1,
            AnomalySeverity.WARNING: 2,
            AnomalySeverity.CRITICAL: 3
        }
        return severity_order.get(severity, 0) >= severity_order.get(min_severity, 0)
    
    def _is_in_cooldown(self, alert_key: str) -> bool:
        """Check if alert is in cooldown period."""
        if alert_key not in self._recent_alerts:
            return False
        
        last_alert = self._recent_alerts[alert_key]
        elapsed = (datetime.now() - last_alert).total_seconds()
        return elapsed < self._alert_cooldown_seconds
    
    def _send_slack_alert(self, anomaly: Anomaly, context: RunContext, channel: Dict):
        """Send alert to Slack webhook."""
        webhook_url = channel.get("webhook_url")
        if not webhook_url:
            self.logger.warning("Slack webhook URL not configured")
            return
        
        # Determine emoji based on severity
        emoji_map = {
            AnomalySeverity.INFO: "ℹ️",
            AnomalySeverity.WARNING: "⚠️",
            AnomalySeverity.CRITICAL: "🚨"
        }
        emoji = emoji_map.get(anomaly.severity, "📢")
        
        # Build Slack message
        color_map = {
            AnomalySeverity.INFO: "#36a64f",
            AnomalySeverity.WARNING: "#ff9900",
            AnomalySeverity.CRITICAL: "#ff0000"
        }
        color = color_map.get(anomaly.severity, "#808080")
        
        # Format message
        message = {
            "text": f"{emoji} Automation Run Sentinel Alert",
            "attachments": [
                {
                    "color": color,
                    "title": anomaly.title,
                    "text": anomaly.description,
                    "fields": [
                        {
                            "title": "Run ID",
                            "value": context.run_id,
                            "short": True
                        },
                        {
                            "title": "Pipeline",
                            "value": context.pipeline,
                            "short": True
                        },
                        {
                            "title": "Environment",
                            "value": context.environment,
                            "short": True
                        },
                        {
                            "title": "Severity",
                            "value": anomaly.severity.value.upper(),
                            "short": True
                        },
                        {
                            "title": "Category",
                            "value": anomaly.category.value,
                            "short": True
                        },
                        {
                            "title": "Timestamp",
                            "value": anomaly.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                            "short": True
                        }
                    ],
                    "footer": "Automation Run Sentinel",
                    "ts": int(anomaly.timestamp.timestamp())
                }
            ]
        }
        
        # Add affected component if available
        if anomaly.affected_component:
            message["attachments"][0]["fields"].append({
                "title": "Affected Component",
                "value": anomaly.affected_component,
                "short": True
            })
        
        # Add root cause hints
        if anomaly.root_cause_hints:
            hints_text = "\n".join([f"• {hint}" for hint in anomaly.root_cause_hints])
            message["attachments"][0]["fields"].append({
                "title": "Root Cause Hints",
                "value": hints_text,
                "short": False
            })
        
        # Send to Slack
        try:
            response = requests.post(
                webhook_url,
                json=message,
                timeout=10
            )
            response.raise_for_status()
            self.logger.info(f"Slack alert sent for anomaly {anomaly.anomaly_id}")
        except RequestException as e:
            self.logger.error(f"Failed to send Slack alert: {e}")
            raise
    
    def _send_email_alert(self, anomaly: Anomaly, context: RunContext, channel: Dict):
        """Send alert via email."""
        email_to = channel.get("email_to", [])
        if not email_to:
            self.logger.warning("Email recipients not configured")
            return
        
        try:
            import smtplib
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart
            
            smtp_config = self.config.get("smtp", {})
            smtp_host = smtp_config.get("host", "localhost")
            smtp_port = smtp_config.get("port", 25)
            smtp_user = smtp_config.get("user")
            smtp_password = smtp_config.get("password")
            smtp_from = smtp_config.get("from", "sentinel@example.com")
            
            # Create email
            msg = MIMEMultipart()
            msg["From"] = smtp_from
            msg["To"] = ", ".join(email_to)
            msg["Subject"] = f"[{anomaly.severity.value.upper()}] {anomaly.title}"
            
            # Build email body
            body = f"""
Automation Run Sentinel Alert

Title: {anomaly.title}
Description: {anomaly.description}

Run Information:
- Run ID: {context.run_id}
- Pipeline: {context.pipeline}
- Environment: {context.environment}
- Branch: {context.branch}
- Commit: {context.commit}

Anomaly Details:
- Severity: {anomaly.severity.value}
- Category: {anomaly.category.value}
- Timestamp: {anomaly.timestamp.strftime("%Y-%m-%d %H:%M:%S")}
- Affected Component: {anomaly.affected_component or "N/A"}

Root Cause Hints:
{chr(10).join(f"- {hint}" for hint in anomaly.root_cause_hints) if anomaly.root_cause_hints else "None"}

---
Automation Run Sentinel
"""
            
            msg.attach(MIMEText(body, "plain"))
            
            # Send email
            with smtplib.SMTP(smtp_host, smtp_port) as server:
                if smtp_user and smtp_password:
                    server.login(smtp_user, smtp_password)
                server.send_message(msg)
            
            self.logger.info(f"Email alert sent for anomaly {anomaly.anomaly_id}")
        
        except ImportError:
            self.logger.error("SMTP libraries not available")
        except Exception as e:
            self.logger.error(f"Failed to send email alert: {e}", exc_info=True)
            raise
    
    def _send_webhook_alert(self, anomaly: Anomaly, context: RunContext, channel: Dict):
        """Send alert to generic webhook."""
        webhook_url = channel.get("webhook_url")
        if not webhook_url:
            self.logger.warning("Webhook URL not configured")
            return
        
        # Build payload
        payload = {
            "anomaly": {
                "id": anomaly.anomaly_id,
                "title": anomaly.title,
                "description": anomaly.description,
                "severity": anomaly.severity.value,
                "category": anomaly.category.value,
                "timestamp": anomaly.timestamp.isoformat(),
                "affected_component": anomaly.affected_component,
                "metadata": anomaly.metadata,
                "root_cause_hints": anomaly.root_cause_hints
            },
            "run": {
                "run_id": context.run_id,
                "pipeline": context.pipeline,
                "environment": context.environment,
                "branch": context.branch,
                "commit": context.commit,
                "status": context.status.value
            }
        }
        
        # Send webhook
        try:
            response = requests.post(
                webhook_url,
                json=payload,
                timeout=10,
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            self.logger.info(f"Webhook alert sent for anomaly {anomaly.anomaly_id}")
        except RequestException as e:
            self.logger.error(f"Failed to send webhook alert: {e}")
            raise




