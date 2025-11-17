# Prisma Web App API

**Version:** 1.0.0
**Generated:** 2025-11-06 14:13:32
**Source:** 

## Description

API being used by the Prisma Web App and the desktop application.

## Base URLs

- **Prisma Web App Server** (if provided): `/prisma/api`

## Table of Contents

- [API Endpoints](#api-endpoints)
  - [Alert](#alert)
  - [Login Configuration](#login-configuration)
  - [Map](#map)
  - [Point](#point)
  - [Region](#region)
  - [Role](#role)
  - [User](#user)
- [Schemas](#schemas)
- [Security](#security)

## API Endpoints

Total endpoints: **25**

### Alert

#### `GET` `/{siteId}/api/alert`

**Summary:** No summary

**Operation ID:** `AlertController_findAll`

**Parameters:**

- **startTime** (string, Optional)
  No description
- **endTime** (string, Optional)
  No description
- **classIds** (array, Optional)
  No description
- **severities** (array, Optional)
  No description
- **page** (number, Optional)
  No description
- **isLive** (boolean, Optional)
  No description
- **isLiveView** (boolean, Optional)
  No description
- **orderBy** (string, Optional)
  No description
- **orderByDirection** (string, Optional)
  No description
- **getAlertCount** (boolean, Optional)
  No description
- **regionIds** (array, Optional)
  No description
- **withRegions** (boolean, Optional)
  No description
- **siteId** (string, **Required**)
  No description

**Responses:**

**200** - Either a list of all alerts (if `withAlertCount` is not passed) or an object representing a page of alerts. See the schema for details.
  - **Content-Type:** `application/json`
  - **Type:** `object`

---

#### `DELETE` `/{siteId}/api/alert/delete`

**Summary:** No summary

**Operation ID:** `AlertController_deleteAlerts`

**Parameters:**

- **siteId** (string, **Required**)
  No description

**Request Body:**

**Content-Type:** `application/json`
**Schema:** `DeleteAlertsOptionsDto` (see Schemas section)

**Responses:**

**200** - 

---

#### `GET` `/{siteId}/api/alert/export-alerts`

**Summary:** No summary

**Operation ID:** `AlertController_exportsAlerts`

**Parameters:**

- **startTime** (string, Optional)
  No description
- **endTime** (string, Optional)
  No description
- **classIds** (array, Optional)
  No description
- **severities** (array, Optional)
  No description
- **page** (number, Optional)
  No description
- **isLive** (boolean, Optional)
  No description
- **isLiveView** (boolean, Optional)
  No description
- **orderBy** (string, Optional)
  No description
- **orderByDirection** (string, Optional)
  No description
- **getAlertCount** (boolean, Optional)
  No description
- **regionIds** (array, Optional)
  No description
- **withRegions** (boolean, Optional)
  No description
- **isCSV** (boolean, Optional)
  No description
- **isJSON** (boolean, Optional)
  No description
- **siteId** (string, **Required**)
  No description

**Responses:**

**200** - 

---

#### `GET` `/{siteId}/api/alert/get-alert-status`

**Summary:** No summary

**Operation ID:** `AlertController_getAlertStatus`

**Parameters:**

- **siteId** (string, **Required**)
  No description

**Responses:**

**200** - 

---

### Login Configuration

#### `GET` `/login-configuration`

**Summary:** Get login configuration

**Description:** The externalLoginButtons is a list of all external login buttons which can be supported. Pay attention to the `visible` property, as it can be used to hide buttons for which there are no configured providers.The resetPassword is boolean value indicating whether the reset password feature is enabled.

**Operation ID:** `GetLoginConfiguration`

**Parameters:**

- **successRedirectUrl** (string, Optional) (default: `/`)
  Root-relative URL of the page to redirect in the end of the flow.
- **errorRedirectUrl** (string, Optional) (default: `/externalLoginError`)
  Root-relative URL of the page to redirect in case of an error.

The following query parameters will be appended to it:

#### `errorTraceId`

**Example**: `?errorTraceId=575bfd1e-825c-4ca1-be3b-18e42ea78b61`

The unique identifier that can be provided to support to look up more information about the error.



#### `errorType`

**Example**: `?errorType=userNotMatchedError`

The possible values are:

- `clientError`. The client sent an invalid request, e.g. `successRedirectUrl` is not a valid URL.

- `userNotMatchedError`. We could not match an existing internal user to the external user.

- `loginForbiddenError`. The login was forbidden for the specific user by the access control rules set up by tenant administrator.

- `loginSessionExpiredError`. The login session has expired and its state was lost. Restart login from scratch.

- `providerAccessDeniedError`. The external login provider denied the access to the user. Most likely, the user did not consent to the requested permissions.

- `providerTemporarilyUnavailableError`. The external login provider is temporarily unavailable. Try again later.

- `providerUnknownError`. The external login provider returned an unknown error. Please try again later.

- `internalError`. An internal error occurred. If the issue persists, please contact support providing the `errorTraceId`.



#### `errorMessage`

**Example**: `?errorMessage=We+could+not+match+an+existing+internal+user+to+the+external+user.`

Developer-friendly error message in English.



#### `matchUserAttributes` (optional, array)

**Example**: `?matchUserAttributes=johndoe%40acme.org&matchUserAttributes=jdoe%40acme.onmicrosoft.com`

The attributes of the external user we used to look up the internal user. Will be available only in case of `userNotMatchedError`.



**Responses:**

**200** - Object with external login buttons and reset password login configuration
  - **Content-Type:** `application/json`
  - **Schema:** `BackendLoginConfigurationDto` (see Schemas section)

---

### Map

#### `POST` ⚠️ **DEPRECATED** `/sites/{siteId}/geo-channel-collections!generate`

**Summary:** Generate Geo Channels Collection.

**Description:** [DEPRECATED] Use `Infer Geo Channel Collection from Fiber` instead.Re-generate geo channels collection on a given parameters for a specific site. The created collection is becoming active.

**Operation ID:** `GenerateGeoChannelsCollection`

**Parameters:**

- **siteId** (string, **Required**)
  No description

**Request Body:**

**Content-Type:** `application/json`
**Schema:** `BackendGeoChannelCollectionParamsDto` (see Schemas section)

**Responses:**

**201** - Generated geo channels collection.
  - **Content-Type:** `application/json`
  - **Type:** `array`

**400** - The data provided in the request is invalid. We failed to parse it or there are semantic errors.
  - **Content-Type:** `application/json`
  - **Type:** `object`

**403** - The operation is forbidden due to missing permission `super_admin`. By default, this permission is available for `super admin` role(s).
  - **Content-Type:** `application/json`
  - **Type:** `object`

**404** - Object referenced by the URL path was not found.
  - **Content-Type:** `application/json`
  - **Type:** `object`

**409** - Back-end expected one state in the database, but got something else.
  - **Content-Type:** `application/json`
  - **Type:** `object`

---

#### `POST` `/sites/{siteId}/geo-channel-collections!infer-from-fiber`

**Summary:** Infer Geo Channels Collection from Fiber

**Description:** Creates geo channel collection from fiber points, as they were originally provided in the anchoring file. The created collection becomes active.

* Fiber points are sorted by DoF in ascending order.

* Points with the same GPS coordinate are skipped.

* Geo channel number is inferred from the order of the point in the list (when they are sorted by DoF and duplicates removed).

**Operation ID:** `InferGeoChannelsCollectionFromFiber`

**Parameters:**

- **siteId** (string, **Required**)
  No description

**Responses:**

**201** - Generated geo channel collection.
  - **Content-Type:** `application/json`
  - **Schema:** `BackendGeoChannelCollectionDto` (see Schemas section)

**403** - The operation is forbidden due to missing permission `super_admin`. By default, this permission is available for `super admin` role(s).
  - **Content-Type:** `application/json`
  - **Type:** `object`

**404** - Object referenced by the URL path was not found.
  - **Content-Type:** `application/json`
  - **Type:** `object`

**409** - Back-end expected one state in the database, but got something else.
  - **Content-Type:** `application/json`
  - **Type:** `object`

---

#### `GET` `/{siteId}/api/site/get-sites`

**Summary:** No summary

**Operation ID:** `SiteController_findAll`

**Parameters:**

- **siteId** (string, **Required**)
  No description

**Responses:**

**200** - 

---

### Point

#### `GET` `/{siteId}/api/point/map-setup`

**Summary:** No summary

**Operation ID:** `PointController_findAll`

**Parameters:**

- **siteId** (string, **Required**)
  No description

**Responses:**

**200** - 

---

### Region

#### `GET` `/{siteId}/api/region`

**Summary:** No summary

**Operation ID:** `RegionController_getAllRegions`

**Parameters:**

- **withGeneral** (boolean, Optional)
  No description

**Responses:**

**200** - 
  - **Content-Type:** `application/json`
  - **Type:** `array`

---

#### `POST` `/{siteId}/api/region/add`

**Summary:** No summary

**Operation ID:** `RegionController_addRegion`

**Parameters:**

- **siteId** (string, **Required**)
  No description

**Request Body:**

**Content-Type:** `application/json`
**Schema:** `RegionCreateDto` (see Schemas section)

**Responses:**

**201** - 

---

#### `POST` `/{siteId}/api/region/update`

**Summary:** No summary

**Operation ID:** `RegionController_updateRegion`

**Parameters:**

- **siteId** (string, **Required**)
  No description

**Request Body:**

**Content-Type:** `application/json`
**Schema:** `RegionCreateDto` (see Schemas section)

**Responses:**

**201** - 

---

#### `DELETE` `/{siteId}/api/region/{id}`

**Summary:** No summary

**Operation ID:** `RegionController_deleteRegion`

**Parameters:**

- **id** (string, **Required**)
  No description

**Responses:**

**200** - 

---

### Role

#### `GET` `/{siteId}/api/role`

**Summary:** No summary

**Operation ID:** `RoleController_getAllRoles`

**Parameters:**

- **siteId** (string, **Required**)
  No description

**Responses:**

**200** - 
  - **Content-Type:** `application/json`
  - **Type:** `array`

---

### User

#### `POST` `/users/{userId}!delete-external-identities`

**Summary:** Delete External User Identities

**Description:** Deletes selected external user identities. Next time the user logs in, the internal <-> external user association will be performed based on user attributes, e.g. username or email.

**Operation ID:** `DeleteExternalUserIdentities`

**Parameters:**

- **userId** (string, **Required**)
  No description

**Request Body:**

**Content-Type:** `application/json`
**Schema:** `BackendDeleteExternalUserIdentitiesCommandBodyDto` (see Schemas section)

**Responses:**

**200** - Updated user object with changed identities.
  - **Content-Type:** `application/json`
  - **Schema:** `BackendUserDto` (see Schemas section)

**400** - Unsupported identity type provided.
  - **Content-Type:** `application/json`
  - **Type:** `object`

**404** - User was not found.
  - **Content-Type:** `application/json`
  - **Type:** `object`

**409** - One or more of the provided identities to delete were not found.
  - **Content-Type:** `application/json`
  - **Type:** `object`

---

#### `POST` `/users/{userId}!toggle-login`

**Summary:** Toggle User Login

**Description:** Forbids or allows login with certain identities for a given user.

**Operation ID:** `ToggleUserLogin`

**Parameters:**

- **userId** (string, **Required**)
  No description

**Request Body:**

**Content-Type:** `application/json`
**Schema:** `BackendToggleUserIdentityLoginCommandBodyDto` (see Schemas section)

**Responses:**

**200** - Updated user object with changed identities.
  - **Content-Type:** `application/json`
  - **Schema:** `BackendUserDto` (see Schemas section)

**403** - The operation is forbidden due to missing permission `user_identity__write`. By default, this permission is available for `super admin`, `admin` role(s).
  - **Content-Type:** `application/json`
  - **Type:** `object`

**404** - User was not found.
  - **Content-Type:** `application/json`
  - **Type:** `object`

**409** - One or more of the provided identities to update were not found.
  - **Content-Type:** `application/json`
  - **Type:** `object`

---

#### `POST` `/{siteId}/api/user/add-permission-to-role`

**Summary:** No summary

**Operation ID:** `LegacyUserController_addPermissionToRole`

**Parameters:**

- **size** (unknown type)

**Request Body:**

**Content-Type:** `application/json`
**Schema:** `addPermissionToRoleDto` (see Schemas section)

**Responses:**

**201** - 

---

#### `GET` `/{siteId}/api/user/config`

**Operation ID:** `GetLegacyUserConfiguration`

**Parameters:**

- **siteId** (string, **Required**)
  No description

**Responses:**

**200** - 
  - **Content-Type:** `application/json`
  - **Schema:** `BackendUserConfigViewDto` (see Schemas section)

---

#### `POST` `/{siteId}/api/user/delete`

**Summary:** No summary

**Operation ID:** `LegacyUserController_deleteUser`

**Parameters:**

- **siteId** (string, **Required**)
  No description

**Request Body:**

**Content-Type:** `application/json`
**Schema:** `DeleteUserDto` (see Schemas section)

**Responses:**

**201** - 

---

#### `GET` `/{siteId}/api/user/get-all-users`

**Summary:** No summary

**Operation ID:** `LegacyUserController_getAllUsers`

**Parameters:**

- **getSetting** (boolean, **Required**)
  No description

**Responses:**

**200** - 
  - **Content-Type:** `application/json`
  - **Type:** `array`

---

#### `POST` `/{siteId}/api/user/sign-up`

**Summary:** No summary

**Operation ID:** `LegacyUserController_signUp`

**Parameters:**

- **siteId** (string, **Required**)
  No description

**Request Body:**

**Content-Type:** `application/json`
**Schema:** `CreateUserWithNotificationSettingDto` (see Schemas section)

**Responses:**

**201** - 

---

#### `POST` `/{siteId}/api/user/update`

**Summary:** No summary

**Operation ID:** `LegacyUserController_updateUser`

**Parameters:**

- **siteId** (string, **Required**)
  No description

**Request Body:**

**Content-Type:** `application/json`
**Schema:** `UpdateUserWithNotificationSettingDto` (see Schemas section)

**Responses:**

**201** - 

---

#### `POST` `/{siteId}/api/user/update-other-user`

**Summary:** No summary

**Operation ID:** `LegacyUserController_updateOtherUser`

**Parameters:**

- **siteId** (string, **Required**)
  No description

**Request Body:**

**Content-Type:** `application/json`
**Schema:** `UpdateUserWithNotificationSettingDto` (see Schemas section)

**Responses:**

**201** - 

---

#### `POST` `/{siteId}/api/user/validate-email`

**Summary:** No summary

**Operation ID:** `LegacyUserController_validateEmail`

**Parameters:**

- **siteId** (string, **Required**)
  No description

**Request Body:**

**Content-Type:** `application/json`
**Schema:** `ValidateEmailDto` (see Schemas section)

**Responses:**

**201** - 

---

#### `POST` `/{siteId}/api/user/validate-username`

**Summary:** No summary

**Operation ID:** `LegacyUserController_validateUsername`

**Parameters:**

- **siteId** (string, **Required**)
  No description

**Request Body:**

**Content-Type:** `application/json`
**Schema:** `ValidateUsernameDto` (see Schemas section)

**Responses:**

**201** - 

---

## Schemas

Total schemas: **8**

### BackendDeleteExternalUserIdentitiesCommandBodyDto

**Type:** `object`

**Properties:**

- **identitiesToDelete** (`array`, **Required**)

---

### BackendExternalUserIdentityReferenceDto

**Type:** `object`

**Properties:**

- **id** (`string`, **Required**)
  - Id of the API resource, converted to a string.

- **type** (`string`, **Required**)
  - Type of the API resource.
  - **Allowed values:** `MicrosoftEntraUserIdentity`

---

### BackendRoleListEntryDto

**Type:** `object`

**Properties:**

- **createTime** (`string`, **Required**)

- **id** (`number`, **Required**)

- **permissions** (`array`, **Required**)

- **region** (`string`, **Required**)

- **type** (`string`, **Required**)
  - **Allowed values:** `super admin`, `admin`, `viewer`

- **updateTime** (`string`, **Required**)

---

### DeleteAlertsOptionsDto

**Type:** `object`

**Properties:**

- **alertIds** (`array`, **Required**)

---

### DeleteExternalUserIdentities404Error_NotFoundError

**Type:** `object`

**Properties:**

- **message** (`string`, **Required**)

- **path** (`string`, **Required**)
  - HTTP path where the error happened.

- **statusCode** (`number`, **Required**)
  -  Always set to '404'.
  - **Allowed values:** `404`

- **timestamp** (`string`, **Required**)
  - When the error happened.

- **type** (`string`, **Required**)
  - The type of the object. Always set to `NotFoundError`.
  - **Allowed values:** `NotFoundError`

---

### RegionCreateDto

**Type:** `object`

**Properties:**

- **id** (`number`, **Required**)

- **name** (`string`, **Required**)

- **points** (`array`, **Required**)

---

### RegionEntity

**Type:** `object`

---

### V1BackendAlertPageDto

**Type:** `object`

**Properties:**

- **alerts** (`array`, **Required**)

- **alertsCount** (`number`, **Required**)

- **maxPage** (`number`, **Required**)

---

## Security

### Security Schemes

#### cookie

**Type:** `apiKey`

---
