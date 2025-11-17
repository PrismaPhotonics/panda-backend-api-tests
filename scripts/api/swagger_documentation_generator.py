"""
Swagger API Documentation Generator

This script fetches the Swagger/OpenAPI specification from the Focus Server API
and generates a comprehensive documentation document with all endpoints, methods,
parameters, responses, and schemas.

Author: QA Automation Team
Date: 2025-11-04
"""

import requests
import json
import yaml
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime
import urllib3
import sys

# Fix encoding for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Disable SSL warnings for self-signed certificates
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class SwaggerDocumentationGenerator:
    """Generates comprehensive API documentation from Swagger/OpenAPI specification."""
    
    def __init__(self, swagger_url: str, output_dir: str = "docs/03_architecture/api"):
        """
        Initialize the documentation generator.
        
        Args:
            swagger_url: URL to the Swagger JSON endpoint
            output_dir: Directory to save the generated documentation
        """
        self.swagger_url = swagger_url
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.spec = None
        
    def fetch_swagger_spec(self, base_url: str = None) -> Dict[str, Any]:
        """
        Fetch the Swagger/OpenAPI specification from the server.
        
        Args:
            base_url: Base URL to try different Swagger endpoints. If None, uses self.swagger_url
            
        Returns:
            Dictionary containing the Swagger specification
            
        Raises:
            requests.RequestException: If the request fails
        """
        # Try multiple common Swagger JSON endpoints
        possible_paths = [
            '/api/swagger.json',
            '/swagger.json',
            '/api/swagger/v1/swagger.json',
            '/swagger/v1/swagger.json',
            '/openapi.json',
            '/api/openapi.json',
            '/swagger/swagger.json',
            '/focus-server/api/swagger.json',
            '/focus-server/swagger.json',
            '/api/swagger/v1/swagger.json',
            '/api/v1/swagger.json',
            '/v1/swagger.json',
            '/swagger/v1/swagger.json',
            '/api/swagger/swagger.json',
            '/swagger/swagger/v1/swagger.json'
        ]
        
        if base_url is None:
            # Extract base URL from self.swagger_url
            if self.swagger_url.endswith('.json'):
                base_url = self.swagger_url.rsplit('/', 1)[0]
            else:
                base_url = self.swagger_url.rstrip('/')
        
        urls_to_try = [base_url + path for path in possible_paths]
        
        last_error = None
        for url in urls_to_try:
            print(f"Trying: {url}")
            try:
                response = requests.get(
                    url,
                    verify=False,  # Self-signed certificate
                    timeout=30
                )
                response.raise_for_status()
                self.spec = response.json()
                
                # Validate it's a Swagger/OpenAPI spec
                if 'openapi' in self.spec or 'swagger' in self.spec:
                    print(f"[OK] Successfully fetched Swagger specification from: {url}")
                    print(f"  - Title: {self.spec.get('info', {}).get('title', 'N/A')}")
                    print(f"  - Version: {self.spec.get('info', {}).get('version', 'N/A')}")
                    print(f"  - Paths: {len(self.spec.get('paths', {}))}")
                    self.swagger_url = url
                    return self.spec
                else:
                    print(f"[SKIP] Response is not a valid Swagger/OpenAPI spec")
            except requests.RequestException as e:
                last_error = e
                print(f"[FAIL] {e}")
                continue
        
        # If all URLs failed, raise the last error
        error_msg = f"Failed to fetch Swagger specification. Tried {len(urls_to_try)} URLs. Last error: {last_error}"
        print(f"[ERROR] {error_msg}")
        raise requests.RequestException(error_msg)
    
    def get_endpoint_summary(self) -> List[Dict[str, Any]]:
        """
        Extract summary of all endpoints from the specification.
        
        Returns:
            List of dictionaries containing endpoint information
        """
        if not self.spec:
            raise ValueError("Swagger specification not loaded. Call fetch_swagger_spec() first.")
        
        endpoints = []
        paths = self.spec.get('paths', {})
        
        for path, path_item in paths.items():
            for method, operation in path_item.items():
                if method in ['get', 'post', 'put', 'delete', 'patch', 'head', 'options']:
                    endpoint_info = {
                        'path': path,
                        'method': method.upper(),
                        'summary': operation.get('summary', 'No summary'),
                        'description': operation.get('description', ''),
                        'operation_id': operation.get('operationId', ''),
                        'tags': operation.get('tags', []),
                        'parameters': operation.get('parameters', []),
                        'request_body': operation.get('requestBody', {}),
                        'responses': operation.get('responses', {}),
                        'deprecated': operation.get('deprecated', False),
                        'security': operation.get('security', [])
                    }
                    endpoints.append(endpoint_info)
        
        return endpoints
    
    def format_parameter(self, param: Dict[str, Any]) -> str:
        """
        Format a parameter definition for documentation.
        
        Args:
            param: Parameter dictionary from Swagger spec
            
        Returns:
            Formatted string representation
        """
        # Handle case where param might be a string or other type
        if not isinstance(param, dict):
            return f"- **{param}** (unknown type)"
        
        schema = param.get('schema', {})
        if isinstance(schema, dict):
            param_type = schema.get('type', 'string')
            default = schema.get('default', '')
        else:
            param_type = 'string'
            default = ''
        
        required = '**Required**' if param.get('required', False) else 'Optional'
        default_str = f" (default: `{default}`)" if default else ""
        
        description = param.get('description', 'No description')
        
        return f"- **{param.get('name', 'unknown')}** ({param_type}, {required}){default_str}\n  {description}"
    
    def format_request_body(self, request_body: Dict[str, Any]) -> str:
        """
        Format request body definition for documentation.
        
        Args:
            request_body: Request body dictionary from Swagger spec
            
        Returns:
            Formatted string representation
        """
        if not request_body:
            return "No request body"
        
        content = request_body.get('content', {})
        if not content:
            return "No content type specified"
        
        result = []
        for content_type, schema_info in content.items():
            result.append(f"**Content-Type:** `{content_type}`")
            schema = schema_info.get('schema', {})
            
            # Handle references
            if '$ref' in schema:
                ref_name = schema['$ref'].split('/')[-1]
                result.append(f"**Schema:** `{ref_name}` (see Schemas section)")
            else:
                result.append(f"**Type:** `{schema.get('type', 'object')}`")
                
                # Include example if available
                example = schema_info.get('example')
                if example:
                    result.append(f"**Example:**\n```json\n{json.dumps(example, indent=2)}\n```")
        
        return "\n".join(result)
    
    def format_response(self, status_code: str, response: Dict[str, Any]) -> str:
        """
        Format response definition for documentation.
        
        Args:
            status_code: HTTP status code
            response: Response dictionary from Swagger spec
            
        Returns:
            Formatted string representation
        """
        description = response.get('description', 'No description')
        content = response.get('content', {})
        
        result = [f"**{status_code}** - {description}"]
        
        if content:
            for content_type, schema_info in content.items():
                schema = schema_info.get('schema', {})
                
                if '$ref' in schema:
                    ref_name = schema['$ref'].split('/')[-1]
                    result.append(f"  - **Content-Type:** `{content_type}`")
                    result.append(f"  - **Schema:** `{ref_name}` (see Schemas section)")
                else:
                    result.append(f"  - **Content-Type:** `{content_type}`")
                    result.append(f"  - **Type:** `{schema.get('type', 'object')}`")
        
        return "\n".join(result)
    
    def generate_markdown_documentation(self) -> str:
        """
        Generate comprehensive Markdown documentation from Swagger specification.
        
        Returns:
            Complete Markdown documentation as string
        """
        if not self.spec:
            raise ValueError("Swagger specification not loaded. Call fetch_swagger_spec() first.")
        
        info = self.spec.get('info', {})
        servers = self.spec.get('servers', [])
        endpoints = self.get_endpoint_summary()
        
        # Group endpoints by tags
        endpoints_by_tag = {}
        for endpoint in endpoints:
            tags = endpoint['tags'] if endpoint['tags'] else ['Untagged']
            for tag in tags:
                if tag not in endpoints_by_tag:
                    endpoints_by_tag[tag] = []
                endpoints_by_tag[tag].append(endpoint)
        
        # Start building the document
        doc_lines = []
        
        # Header
        doc_lines.append(f"# {info.get('title', 'API Documentation')}")
        doc_lines.append("")
        doc_lines.append(f"**Version:** {info.get('version', 'N/A')}")
        doc_lines.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        doc_lines.append(f"**Source:** {self.swagger_url}")
        doc_lines.append("")
        
        # Description
        if info.get('description'):
            doc_lines.append("## Description")
            doc_lines.append("")
            doc_lines.append(info['description'])
            doc_lines.append("")
        
        # Servers
        if servers:
            doc_lines.append("## Base URLs")
            doc_lines.append("")
            for server in servers:
                url = server.get('url', '')
                description = server.get('description', '')
                doc_lines.append(f"- **{description}** (if provided): `{url}`")
            doc_lines.append("")
        
        # Table of Contents
        doc_lines.append("## Table of Contents")
        doc_lines.append("")
        doc_lines.append("- [API Endpoints](#api-endpoints)")
        for tag in sorted(endpoints_by_tag.keys()):
            tag_id = tag.lower().replace(' ', '-')
            doc_lines.append(f"  - [{tag}](#{tag_id})")
        doc_lines.append("- [Schemas](#schemas)")
        doc_lines.append("- [Security](#security)")
        doc_lines.append("")
        
        # API Endpoints
        doc_lines.append("## API Endpoints")
        doc_lines.append("")
        doc_lines.append(f"Total endpoints: **{len(endpoints)}**")
        doc_lines.append("")
        
        # Endpoints by tag
        for tag in sorted(endpoints_by_tag.keys()):
            tag_id = tag.lower().replace(' ', '-')
            doc_lines.append(f"### {tag}")
            doc_lines.append("")
            
            for endpoint in sorted(endpoints_by_tag[tag], key=lambda x: (x['path'], x['method'])):
                # Endpoint header
                method_badge = f"`{endpoint['method']}`"
                if endpoint['deprecated']:
                    method_badge += " ⚠️ **DEPRECATED**"
                
                doc_lines.append(f"#### {method_badge} `{endpoint['path']}`")
                doc_lines.append("")
                
                # Summary and description
                if endpoint['summary']:
                    doc_lines.append(f"**Summary:** {endpoint['summary']}")
                    doc_lines.append("")
                
                if endpoint['description']:
                    doc_lines.append(f"**Description:** {endpoint['description']}")
                    doc_lines.append("")
                
                # Operation ID
                if endpoint['operation_id']:
                    doc_lines.append(f"**Operation ID:** `{endpoint['operation_id']}`")
                    doc_lines.append("")
                
                # Parameters
                if endpoint['parameters']:
                    doc_lines.append("**Parameters:**")
                    doc_lines.append("")
                    for param in endpoint['parameters']:
                        doc_lines.append(self.format_parameter(param))
                    doc_lines.append("")
                
                # Request Body
                if endpoint['request_body']:
                    doc_lines.append("**Request Body:**")
                    doc_lines.append("")
                    doc_lines.append(self.format_request_body(endpoint['request_body']))
                    doc_lines.append("")
                
                # Responses
                if endpoint['responses']:
                    doc_lines.append("**Responses:**")
                    doc_lines.append("")
                    for status_code, response in sorted(endpoint['responses'].items()):
                        doc_lines.append(self.format_response(status_code, response))
                        doc_lines.append("")
                
                # Security
                if endpoint['security']:
                    doc_lines.append("**Security:**")
                    doc_lines.append("")
                    for sec in endpoint['security']:
                        doc_lines.append(f"- {json.dumps(sec, indent=2)}")
                    doc_lines.append("")
                
                doc_lines.append("---")
                doc_lines.append("")
        
        # Schemas
        schemas = self.spec.get('components', {}).get('schemas', {})
        if schemas:
            doc_lines.append("## Schemas")
            doc_lines.append("")
            doc_lines.append(f"Total schemas: **{len(schemas)}**")
            doc_lines.append("")
            
            for schema_name, schema_def in sorted(schemas.items()):
                doc_lines.append(f"### {schema_name}")
                doc_lines.append("")
                
                if schema_def.get('description'):
                    doc_lines.append(f"**Description:** {schema_def['description']}")
                    doc_lines.append("")
                
                schema_type = schema_def.get('type', 'object')
                doc_lines.append(f"**Type:** `{schema_type}`")
                doc_lines.append("")
                
                # Properties
                properties = schema_def.get('properties', {})
                if properties:
                    doc_lines.append("**Properties:**")
                    doc_lines.append("")
                    required_fields = schema_def.get('required', [])
                    
                    for prop_name, prop_def in sorted(properties.items()):
                        prop_type = prop_def.get('type', 'string')
                        required = '**Required**' if prop_name in required_fields else 'Optional'
                        description = prop_def.get('description', '')
                        
                        doc_lines.append(f"- **{prop_name}** (`{prop_type}`, {required})")
                        if description:
                            doc_lines.append(f"  - {description}")
                        
                        # Enum values
                        if 'enum' in prop_def:
                            doc_lines.append(f"  - **Allowed values:** {', '.join([f'`{v}`' for v in prop_def['enum']])}")
                        
                        # Default value
                        if 'default' in prop_def:
                            doc_lines.append(f"  - **Default:** `{prop_def['default']}`")
                        
                        doc_lines.append("")
                
                doc_lines.append("---")
                doc_lines.append("")
        
        # Security
        security_schemes = self.spec.get('components', {}).get('securitySchemes', {})
        if security_schemes:
            doc_lines.append("## Security")
            doc_lines.append("")
            doc_lines.append("### Security Schemes")
            doc_lines.append("")
            
            for scheme_name, scheme_def in sorted(security_schemes.items()):
                doc_lines.append(f"#### {scheme_name}")
                doc_lines.append("")
                doc_lines.append(f"**Type:** `{scheme_def.get('type', 'N/A')}`")
                doc_lines.append("")
                
                if scheme_def.get('description'):
                    doc_lines.append(f"**Description:** {scheme_def['description']}")
                    doc_lines.append("")
                
                if scheme_def.get('scheme'):
                    doc_lines.append(f"**Scheme:** `{scheme_def['scheme']}`")
                    doc_lines.append("")
                
                doc_lines.append("---")
                doc_lines.append("")
        
        return "\n".join(doc_lines)
    
    def save_documentation(self, filename: str = None) -> Path:
        """
        Generate and save the documentation to a file.
        
        Args:
            filename: Optional filename. If not provided, auto-generated from API title
            
        Returns:
            Path to the saved documentation file
        """
        if filename is None:
            title = self.spec.get('info', {}).get('title', 'api').lower().replace(' ', '_')
            version = self.spec.get('info', {}).get('version', 'latest')
            filename = f"{title}_documentation_v{version}.md"
        
        output_path = self.output_dir / filename
        
        markdown_content = self.generate_markdown_documentation()
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        print(f"[OK] Documentation saved to: {output_path}")
        return output_path
    
    def save_spec_json(self, filename: str = "swagger_spec.json") -> Path:
        """
        Save the raw Swagger specification as JSON for reference.
        
        Args:
            filename: Filename for the JSON file
            
        Returns:
            Path to the saved JSON file
        """
        output_path = self.output_dir / filename
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.spec, f, indent=2, ensure_ascii=False)
        
        print(f"[OK] Raw specification saved to: {output_path}")
        return output_path


def main():
    """Main execution function."""
    # Try to load from saved JSON file first
    saved_spec_path = Path("docs/03_architecture/api/swagger_spec.json")
    output_dir = "docs/03_architecture/api"
    
    print("=" * 80)
    print("Swagger API Documentation Generator")
    print("=" * 80)
    print()
    
    try:
        # Initialize generator
        generator = SwaggerDocumentationGenerator("", output_dir)
        
        # Try to load from saved file
        if saved_spec_path.exists():
            print(f"Loading Swagger specification from saved file: {saved_spec_path}")
            with open(saved_spec_path, 'r', encoding='utf-8') as f:
                generator.spec = json.load(f)
            print(f"[OK] Loaded specification from file")
            print(f"  - Title: {generator.spec.get('info', {}).get('title', 'N/A')}")
            print(f"  - Version: {generator.spec.get('info', {}).get('version', 'N/A')}")
            print(f"  - Paths: {len(generator.spec.get('paths', {}))}")
        else:
            # Try to fetch from server
            base_url = "https://10.10.100.100"
            generator.fetch_swagger_spec(base_url=base_url)
        
        # Generate and save documentation
        doc_path = generator.save_documentation()
        
        # Save raw specification
        spec_path = generator.save_spec_json()
        
        print()
        print("=" * 80)
        print("[SUCCESS] Documentation generation completed successfully!")
        print("=" * 80)
        print(f"Documentation: {doc_path}")
        print(f"Raw Spec: {spec_path}")
        
    except Exception as e:
        print()
        print("=" * 80)
        print(f"[ERROR] {e}")
        print("=" * 80)
        raise


if __name__ == "__main__":
    main()

