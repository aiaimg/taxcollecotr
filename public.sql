/*
 Navicat Premium Dump SQL

 Source Server         : vms
 Source Server Type    : PostgreSQL
 Source Server Version : 170005 (170005)
 Source Host           : localhost:5432
 Source Catalog        : taxcollector
 Source Schema         : public

 Target Server Type    : PostgreSQL
 Target Server Version : 170005 (170005)
 File Encoding         : 65001

 Date: 06/11/2025 16:40:46
*/


-- ----------------------------
-- Sequence structure for account_emailaddress_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "public"."account_emailaddress_id_seq";
CREATE SEQUENCE "public"."account_emailaddress_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 2147483647
START 1
CACHE 1;

-- ----------------------------
-- Sequence structure for account_emailconfirmation_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "public"."account_emailconfirmation_id_seq";
CREATE SEQUENCE "public"."account_emailconfirmation_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 2147483647
START 1
CACHE 1;

-- ----------------------------
-- Sequence structure for administration_adminsession_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "public"."administration_adminsession_id_seq";
CREATE SEQUENCE "public"."administration_adminsession_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 9223372036854775807
START 1
CACHE 1;

-- ----------------------------
-- Sequence structure for administration_adminuserprofile_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "public"."administration_adminuserprofile_id_seq";
CREATE SEQUENCE "public"."administration_adminuserprofile_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 9223372036854775807
START 1
CACHE 1;

-- ----------------------------
-- Sequence structure for administration_agentverification_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "public"."administration_agentverification_id_seq";
CREATE SEQUENCE "public"."administration_agentverification_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 9223372036854775807
START 1
CACHE 1;

-- ----------------------------
-- Sequence structure for administration_configurationsysteme_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "public"."administration_configurationsysteme_id_seq";
CREATE SEQUENCE "public"."administration_configurationsysteme_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 9223372036854775807
START 1
CACHE 1;

-- ----------------------------
-- Sequence structure for administration_dataversion_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "public"."administration_dataversion_id_seq";
CREATE SEQUENCE "public"."administration_dataversion_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 9223372036854775807
START 1
CACHE 1;

-- ----------------------------
-- Sequence structure for administration_permissiongroup_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "public"."administration_permissiongroup_id_seq";
CREATE SEQUENCE "public"."administration_permissiongroup_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 9223372036854775807
START 1
CACHE 1;

-- ----------------------------
-- Sequence structure for administration_permissiongroup_users_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "public"."administration_permissiongroup_users_id_seq";
CREATE SEQUENCE "public"."administration_permissiongroup_users_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 9223372036854775807
START 1
CACHE 1;

-- ----------------------------
-- Sequence structure for administration_statistiquesplateforme_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "public"."administration_statistiquesplateforme_id_seq";
CREATE SEQUENCE "public"."administration_statistiquesplateforme_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 9223372036854775807
START 1
CACHE 1;

-- ----------------------------
-- Sequence structure for auth_group_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "public"."auth_group_id_seq";
CREATE SEQUENCE "public"."auth_group_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 2147483647
START 1
CACHE 1;

-- ----------------------------
-- Sequence structure for auth_group_permissions_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "public"."auth_group_permissions_id_seq";
CREATE SEQUENCE "public"."auth_group_permissions_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 9223372036854775807
START 1
CACHE 1;

-- ----------------------------
-- Sequence structure for auth_permission_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "public"."auth_permission_id_seq";
CREATE SEQUENCE "public"."auth_permission_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 2147483647
START 1
CACHE 1;

-- ----------------------------
-- Sequence structure for auth_user_groups_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "public"."auth_user_groups_id_seq";
CREATE SEQUENCE "public"."auth_user_groups_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 9223372036854775807
START 1
CACHE 1;

-- ----------------------------
-- Sequence structure for auth_user_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "public"."auth_user_id_seq";
CREATE SEQUENCE "public"."auth_user_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 2147483647
START 1
CACHE 1;

-- ----------------------------
-- Sequence structure for auth_user_user_permissions_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "public"."auth_user_user_permissions_id_seq";
CREATE SEQUENCE "public"."auth_user_user_permissions_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 9223372036854775807
START 1
CACHE 1;

-- ----------------------------
-- Sequence structure for django_admin_log_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "public"."django_admin_log_id_seq";
CREATE SEQUENCE "public"."django_admin_log_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 2147483647
START 1
CACHE 1;

-- ----------------------------
-- Sequence structure for django_content_type_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "public"."django_content_type_id_seq";
CREATE SEQUENCE "public"."django_content_type_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 2147483647
START 1
CACHE 1;

-- ----------------------------
-- Sequence structure for django_migrations_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "public"."django_migrations_id_seq";
CREATE SEQUENCE "public"."django_migrations_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 9223372036854775807
START 1
CACHE 1;

-- ----------------------------
-- Sequence structure for django_site_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "public"."django_site_id_seq";
CREATE SEQUENCE "public"."django_site_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 2147483647
START 1
CACHE 1;

-- ----------------------------
-- Sequence structure for notifications_notificationtemplate_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "public"."notifications_notificationtemplate_id_seq";
CREATE SEQUENCE "public"."notifications_notificationtemplate_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 9223372036854775807
START 1
CACHE 1;

-- ----------------------------
-- Sequence structure for payments_stripeconfig_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "public"."payments_stripeconfig_id_seq";
CREATE SEQUENCE "public"."payments_stripeconfig_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 9223372036854775807
START 1
CACHE 1;

-- ----------------------------
-- Sequence structure for payments_stripewebhookevent_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "public"."payments_stripewebhookevent_id_seq";
CREATE SEQUENCE "public"."payments_stripewebhookevent_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 9223372036854775807
START 1
CACHE 1;

-- ----------------------------
-- Sequence structure for socialaccount_socialaccount_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "public"."socialaccount_socialaccount_id_seq";
CREATE SEQUENCE "public"."socialaccount_socialaccount_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 2147483647
START 1
CACHE 1;

-- ----------------------------
-- Sequence structure for socialaccount_socialapp_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "public"."socialaccount_socialapp_id_seq";
CREATE SEQUENCE "public"."socialaccount_socialapp_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 2147483647
START 1
CACHE 1;

-- ----------------------------
-- Sequence structure for socialaccount_socialapp_sites_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "public"."socialaccount_socialapp_sites_id_seq";
CREATE SEQUENCE "public"."socialaccount_socialapp_sites_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 9223372036854775807
START 1
CACHE 1;

-- ----------------------------
-- Sequence structure for socialaccount_socialtoken_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "public"."socialaccount_socialtoken_id_seq";
CREATE SEQUENCE "public"."socialaccount_socialtoken_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 2147483647
START 1
CACHE 1;

-- ----------------------------
-- Sequence structure for vehicles_grilletarifaire_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "public"."vehicles_grilletarifaire_id_seq";
CREATE SEQUENCE "public"."vehicles_grilletarifaire_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 9223372036854775807
START 1
CACHE 1;

-- ----------------------------
-- Sequence structure for vehicles_vehicletype_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "public"."vehicles_vehicletype_id_seq";
CREATE SEQUENCE "public"."vehicles_vehicletype_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 9223372036854775807
START 1
CACHE 1;

-- ----------------------------
-- Table structure for account_emailaddress
-- ----------------------------
DROP TABLE IF EXISTS "public"."account_emailaddress";
CREATE TABLE "public"."account_emailaddress" (
  "id" int4 NOT NULL GENERATED BY DEFAULT AS IDENTITY (
INCREMENT 1
MINVALUE  1
MAXVALUE 2147483647
START 1
CACHE 1
),
  "email" varchar(254) COLLATE "pg_catalog"."default" NOT NULL,
  "verified" bool NOT NULL,
  "primary" bool NOT NULL,
  "user_id" int4 NOT NULL
)
;

-- ----------------------------
-- Records of account_emailaddress
-- ----------------------------

-- ----------------------------
-- Table structure for account_emailconfirmation
-- ----------------------------
DROP TABLE IF EXISTS "public"."account_emailconfirmation";
CREATE TABLE "public"."account_emailconfirmation" (
  "id" int4 NOT NULL GENERATED BY DEFAULT AS IDENTITY (
INCREMENT 1
MINVALUE  1
MAXVALUE 2147483647
START 1
CACHE 1
),
  "created" timestamptz(6) NOT NULL,
  "sent" timestamptz(6),
  "key" varchar(64) COLLATE "pg_catalog"."default" NOT NULL,
  "email_address_id" int4 NOT NULL
)
;

-- ----------------------------
-- Records of account_emailconfirmation
-- ----------------------------

-- ----------------------------
-- Table structure for administration_adminsession
-- ----------------------------
DROP TABLE IF EXISTS "public"."administration_adminsession";
CREATE TABLE "public"."administration_adminsession" (
  "id" int8 NOT NULL GENERATED BY DEFAULT AS IDENTITY (
INCREMENT 1
MINVALUE  1
MAXVALUE 9223372036854775807
START 1
CACHE 1
),
  "session_key" varchar(40) COLLATE "pg_catalog"."default" NOT NULL,
  "ip_address" inet NOT NULL,
  "user_agent" text COLLATE "pg_catalog"."default" NOT NULL,
  "created_at" timestamptz(6) NOT NULL,
  "last_activity" timestamptz(6) NOT NULL,
  "is_active" bool NOT NULL,
  "user_id" int4 NOT NULL
)
;

-- ----------------------------
-- Records of administration_adminsession
-- ----------------------------

-- ----------------------------
-- Table structure for administration_adminuserprofile
-- ----------------------------
DROP TABLE IF EXISTS "public"."administration_adminuserprofile";
CREATE TABLE "public"."administration_adminuserprofile" (
  "id" int8 NOT NULL GENERATED BY DEFAULT AS IDENTITY (
INCREMENT 1
MINVALUE  1
MAXVALUE 9223372036854775807
START 1
CACHE 1
),
  "totp_secret" varchar(32) COLLATE "pg_catalog"."default" NOT NULL,
  "is_2fa_enabled" bool NOT NULL,
  "backup_codes" jsonb NOT NULL,
  "ip_whitelist" jsonb NOT NULL,
  "is_ip_whitelist_enabled" bool NOT NULL,
  "last_login_ip" inet,
  "failed_login_attempts" int4 NOT NULL,
  "account_locked_until" timestamptz(6),
  "last_password_change" timestamptz(6),
  "theme_preference" varchar(10) COLLATE "pg_catalog"."default" NOT NULL,
  "created_at" timestamptz(6) NOT NULL,
  "updated_at" timestamptz(6) NOT NULL,
  "user_id" int4 NOT NULL
)
;

-- ----------------------------
-- Records of administration_adminuserprofile
-- ----------------------------

-- ----------------------------
-- Table structure for administration_agentverification
-- ----------------------------
DROP TABLE IF EXISTS "public"."administration_agentverification";
CREATE TABLE "public"."administration_agentverification" (
  "id" int8 NOT NULL GENERATED BY DEFAULT AS IDENTITY (
INCREMENT 1
MINVALUE  1
MAXVALUE 9223372036854775807
START 1
CACHE 1
),
  "numero_badge" varchar(20) COLLATE "pg_catalog"."default" NOT NULL,
  "zone_affectation" varchar(100) COLLATE "pg_catalog"."default" NOT NULL,
  "est_actif" bool NOT NULL,
  "date_creation" timestamptz(6) NOT NULL,
  "date_modification" timestamptz(6) NOT NULL,
  "user_id" int4 NOT NULL
)
;

-- ----------------------------
-- Records of administration_agentverification
-- ----------------------------

-- ----------------------------
-- Table structure for administration_configurationsysteme
-- ----------------------------
DROP TABLE IF EXISTS "public"."administration_configurationsysteme";
CREATE TABLE "public"."administration_configurationsysteme" (
  "id" int8 NOT NULL GENERATED BY DEFAULT AS IDENTITY (
INCREMENT 1
MINVALUE  1
MAXVALUE 9223372036854775807
START 1
CACHE 1
),
  "cle" varchar(100) COLLATE "pg_catalog"."default" NOT NULL,
  "type_config" varchar(50) COLLATE "pg_catalog"."default" NOT NULL,
  "valeur" text COLLATE "pg_catalog"."default" NOT NULL,
  "description" text COLLATE "pg_catalog"."default" NOT NULL,
  "est_actif" bool NOT NULL,
  "date_creation" timestamptz(6) NOT NULL,
  "date_modification" timestamptz(6) NOT NULL,
  "modifie_par_id" int4
)
;

-- ----------------------------
-- Records of administration_configurationsysteme
-- ----------------------------

-- ----------------------------
-- Table structure for administration_dataversion
-- ----------------------------
DROP TABLE IF EXISTS "public"."administration_dataversion";
CREATE TABLE "public"."administration_dataversion" (
  "id" int8 NOT NULL GENERATED BY DEFAULT AS IDENTITY (
INCREMENT 1
MINVALUE  1
MAXVALUE 9223372036854775807
START 1
CACHE 1
),
  "object_id" varchar(50) COLLATE "pg_catalog"."default" NOT NULL,
  "version_number" int4 NOT NULL,
  "data_snapshot" jsonb NOT NULL,
  "changed_at" timestamptz(6) NOT NULL,
  "change_reason" text COLLATE "pg_catalog"."default" NOT NULL,
  "changed_by_id" int4,
  "content_type_id" int4 NOT NULL
)
;

-- ----------------------------
-- Records of administration_dataversion
-- ----------------------------

-- ----------------------------
-- Table structure for administration_permissiongroup
-- ----------------------------
DROP TABLE IF EXISTS "public"."administration_permissiongroup";
CREATE TABLE "public"."administration_permissiongroup" (
  "id" int8 NOT NULL GENERATED BY DEFAULT AS IDENTITY (
INCREMENT 1
MINVALUE  1
MAXVALUE 9223372036854775807
START 1
CACHE 1
),
  "name" varchar(100) COLLATE "pg_catalog"."default" NOT NULL,
  "description" text COLLATE "pg_catalog"."default" NOT NULL,
  "permissions" jsonb NOT NULL,
  "created_at" timestamptz(6) NOT NULL,
  "updated_at" timestamptz(6) NOT NULL,
  "created_by_id" int4
)
;

-- ----------------------------
-- Records of administration_permissiongroup
-- ----------------------------

-- ----------------------------
-- Table structure for administration_permissiongroup_users
-- ----------------------------
DROP TABLE IF EXISTS "public"."administration_permissiongroup_users";
CREATE TABLE "public"."administration_permissiongroup_users" (
  "id" int8 NOT NULL GENERATED BY DEFAULT AS IDENTITY (
INCREMENT 1
MINVALUE  1
MAXVALUE 9223372036854775807
START 1
CACHE 1
),
  "permissiongroup_id" int8 NOT NULL,
  "user_id" int4 NOT NULL
)
;

-- ----------------------------
-- Records of administration_permissiongroup_users
-- ----------------------------

-- ----------------------------
-- Table structure for administration_statistiquesplateforme
-- ----------------------------
DROP TABLE IF EXISTS "public"."administration_statistiquesplateforme";
CREATE TABLE "public"."administration_statistiquesplateforme" (
  "id" int8 NOT NULL GENERATED BY DEFAULT AS IDENTITY (
INCREMENT 1
MINVALUE  1
MAXVALUE 9223372036854775807
START 1
CACHE 1
),
  "type_statistique" varchar(50) COLLATE "pg_catalog"."default" NOT NULL,
  "valeur" numeric(15,2) NOT NULL,
  "date_statistique" date NOT NULL,
  "metadata" jsonb NOT NULL,
  "created_at" timestamptz(6) NOT NULL
)
;

-- ----------------------------
-- Records of administration_statistiquesplateforme
-- ----------------------------

-- ----------------------------
-- Table structure for administration_verificationqr
-- ----------------------------
DROP TABLE IF EXISTS "public"."administration_verificationqr";
CREATE TABLE "public"."administration_verificationqr" (
  "id" uuid NOT NULL,
  "statut_verification" varchar(20) COLLATE "pg_catalog"."default" NOT NULL,
  "date_verification" timestamptz(6) NOT NULL,
  "localisation_gps" jsonb,
  "notes" text COLLATE "pg_catalog"."default" NOT NULL,
  "agent_id" int8 NOT NULL,
  "qr_code_id" uuid NOT NULL
)
;

-- ----------------------------
-- Records of administration_verificationqr
-- ----------------------------

-- ----------------------------
-- Table structure for auth_group
-- ----------------------------
DROP TABLE IF EXISTS "public"."auth_group";
CREATE TABLE "public"."auth_group" (
  "id" int4 NOT NULL GENERATED BY DEFAULT AS IDENTITY (
INCREMENT 1
MINVALUE  1
MAXVALUE 2147483647
START 1
CACHE 1
),
  "name" varchar(150) COLLATE "pg_catalog"."default" NOT NULL
)
;

-- ----------------------------
-- Records of auth_group
-- ----------------------------

-- ----------------------------
-- Table structure for auth_group_permissions
-- ----------------------------
DROP TABLE IF EXISTS "public"."auth_group_permissions";
CREATE TABLE "public"."auth_group_permissions" (
  "id" int8 NOT NULL GENERATED BY DEFAULT AS IDENTITY (
INCREMENT 1
MINVALUE  1
MAXVALUE 9223372036854775807
START 1
CACHE 1
),
  "group_id" int4 NOT NULL,
  "permission_id" int4 NOT NULL
)
;

-- ----------------------------
-- Records of auth_group_permissions
-- ----------------------------

-- ----------------------------
-- Table structure for auth_permission
-- ----------------------------
DROP TABLE IF EXISTS "public"."auth_permission";
CREATE TABLE "public"."auth_permission" (
  "id" int4 NOT NULL GENERATED BY DEFAULT AS IDENTITY (
INCREMENT 1
MINVALUE  1
MAXVALUE 2147483647
START 1
CACHE 1
),
  "name" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "content_type_id" int4 NOT NULL,
  "codename" varchar(100) COLLATE "pg_catalog"."default" NOT NULL
)
;

-- ----------------------------
-- Records of auth_permission
-- ----------------------------
INSERT INTO "public"."auth_permission" VALUES (1, 'Can add log entry', 1, 'add_logentry');
INSERT INTO "public"."auth_permission" VALUES (2, 'Can change log entry', 1, 'change_logentry');
INSERT INTO "public"."auth_permission" VALUES (3, 'Can delete log entry', 1, 'delete_logentry');
INSERT INTO "public"."auth_permission" VALUES (4, 'Can view log entry', 1, 'view_logentry');
INSERT INTO "public"."auth_permission" VALUES (5, 'Can add permission', 2, 'add_permission');
INSERT INTO "public"."auth_permission" VALUES (6, 'Can change permission', 2, 'change_permission');
INSERT INTO "public"."auth_permission" VALUES (7, 'Can delete permission', 2, 'delete_permission');
INSERT INTO "public"."auth_permission" VALUES (8, 'Can view permission', 2, 'view_permission');
INSERT INTO "public"."auth_permission" VALUES (9, 'Can add group', 3, 'add_group');
INSERT INTO "public"."auth_permission" VALUES (10, 'Can change group', 3, 'change_group');
INSERT INTO "public"."auth_permission" VALUES (11, 'Can delete group', 3, 'delete_group');
INSERT INTO "public"."auth_permission" VALUES (12, 'Can view group', 3, 'view_group');
INSERT INTO "public"."auth_permission" VALUES (13, 'Can add user', 4, 'add_user');
INSERT INTO "public"."auth_permission" VALUES (14, 'Can change user', 4, 'change_user');
INSERT INTO "public"."auth_permission" VALUES (15, 'Can delete user', 4, 'delete_user');
INSERT INTO "public"."auth_permission" VALUES (16, 'Can view user', 4, 'view_user');
INSERT INTO "public"."auth_permission" VALUES (17, 'Can add content type', 5, 'add_contenttype');
INSERT INTO "public"."auth_permission" VALUES (18, 'Can change content type', 5, 'change_contenttype');
INSERT INTO "public"."auth_permission" VALUES (19, 'Can delete content type', 5, 'delete_contenttype');
INSERT INTO "public"."auth_permission" VALUES (20, 'Can view content type', 5, 'view_contenttype');
INSERT INTO "public"."auth_permission" VALUES (21, 'Can add session', 6, 'add_session');
INSERT INTO "public"."auth_permission" VALUES (22, 'Can change session', 6, 'change_session');
INSERT INTO "public"."auth_permission" VALUES (23, 'Can delete session', 6, 'delete_session');
INSERT INTO "public"."auth_permission" VALUES (24, 'Can view session', 6, 'view_session');
INSERT INTO "public"."auth_permission" VALUES (25, 'Can add Log d''audit', 7, 'add_auditlog');
INSERT INTO "public"."auth_permission" VALUES (26, 'Can change Log d''audit', 7, 'change_auditlog');
INSERT INTO "public"."auth_permission" VALUES (27, 'Can delete Log d''audit', 7, 'delete_auditlog');
INSERT INTO "public"."auth_permission" VALUES (28, 'Can view Log d''audit', 7, 'view_auditlog');
INSERT INTO "public"."auth_permission" VALUES (29, 'Can add Profil entreprise', 8, 'add_entrepriseprofile');
INSERT INTO "public"."auth_permission" VALUES (30, 'Can change Profil entreprise', 8, 'change_entrepriseprofile');
INSERT INTO "public"."auth_permission" VALUES (31, 'Can delete Profil entreprise', 8, 'delete_entrepriseprofile');
INSERT INTO "public"."auth_permission" VALUES (32, 'Can view Profil entreprise', 8, 'view_entrepriseprofile');
INSERT INTO "public"."auth_permission" VALUES (33, 'Can add Profil utilisateur', 9, 'add_userprofile');
INSERT INTO "public"."auth_permission" VALUES (34, 'Can change Profil utilisateur', 9, 'change_userprofile');
INSERT INTO "public"."auth_permission" VALUES (35, 'Can delete Profil utilisateur', 9, 'delete_userprofile');
INSERT INTO "public"."auth_permission" VALUES (36, 'Can view Profil utilisateur', 9, 'view_userprofile');
INSERT INTO "public"."auth_permission" VALUES (37, 'Can add Grille tarifaire', 10, 'add_grilletarifaire');
INSERT INTO "public"."auth_permission" VALUES (38, 'Can change Grille tarifaire', 10, 'change_grilletarifaire');
INSERT INTO "public"."auth_permission" VALUES (39, 'Can delete Grille tarifaire', 10, 'delete_grilletarifaire');
INSERT INTO "public"."auth_permission" VALUES (40, 'Can view Grille tarifaire', 10, 'view_grilletarifaire');
INSERT INTO "public"."auth_permission" VALUES (41, 'Can add Véhicule', 11, 'add_vehicule');
INSERT INTO "public"."auth_permission" VALUES (42, 'Can change Véhicule', 11, 'change_vehicule');
INSERT INTO "public"."auth_permission" VALUES (43, 'Can delete Véhicule', 11, 'delete_vehicule');
INSERT INTO "public"."auth_permission" VALUES (44, 'Can view Véhicule', 11, 'view_vehicule');
INSERT INTO "public"."auth_permission" VALUES (45, 'Can add Paiement de taxe', 12, 'add_paiementtaxe');
INSERT INTO "public"."auth_permission" VALUES (46, 'Can change Paiement de taxe', 12, 'change_paiementtaxe');
INSERT INTO "public"."auth_permission" VALUES (47, 'Can delete Paiement de taxe', 12, 'delete_paiementtaxe');
INSERT INTO "public"."auth_permission" VALUES (48, 'Can view Paiement de taxe', 12, 'view_paiementtaxe');
INSERT INTO "public"."auth_permission" VALUES (49, 'Can add QR Code', 13, 'add_qrcode');
INSERT INTO "public"."auth_permission" VALUES (50, 'Can change QR Code', 13, 'change_qrcode');
INSERT INTO "public"."auth_permission" VALUES (51, 'Can delete QR Code', 13, 'delete_qrcode');
INSERT INTO "public"."auth_permission" VALUES (52, 'Can view QR Code', 13, 'view_qrcode');
INSERT INTO "public"."auth_permission" VALUES (53, 'Can add Template de notification', 14, 'add_notificationtemplate');
INSERT INTO "public"."auth_permission" VALUES (54, 'Can change Template de notification', 14, 'change_notificationtemplate');
INSERT INTO "public"."auth_permission" VALUES (55, 'Can delete Template de notification', 14, 'delete_notificationtemplate');
INSERT INTO "public"."auth_permission" VALUES (56, 'Can view Template de notification', 14, 'view_notificationtemplate');
INSERT INTO "public"."auth_permission" VALUES (57, 'Can add Notification', 15, 'add_notification');
INSERT INTO "public"."auth_permission" VALUES (58, 'Can change Notification', 15, 'change_notification');
INSERT INTO "public"."auth_permission" VALUES (59, 'Can delete Notification', 15, 'delete_notification');
INSERT INTO "public"."auth_permission" VALUES (60, 'Can view Notification', 15, 'view_notification');
INSERT INTO "public"."auth_permission" VALUES (61, 'Can add Agent de vérification', 16, 'add_agentverification');
INSERT INTO "public"."auth_permission" VALUES (62, 'Can change Agent de vérification', 16, 'change_agentverification');
INSERT INTO "public"."auth_permission" VALUES (63, 'Can delete Agent de vérification', 16, 'delete_agentverification');
INSERT INTO "public"."auth_permission" VALUES (64, 'Can view Agent de vérification', 16, 'view_agentverification');
INSERT INTO "public"."auth_permission" VALUES (65, 'Can add Configuration système', 17, 'add_configurationsysteme');
INSERT INTO "public"."auth_permission" VALUES (66, 'Can change Configuration système', 17, 'change_configurationsysteme');
INSERT INTO "public"."auth_permission" VALUES (67, 'Can delete Configuration système', 17, 'delete_configurationsysteme');
INSERT INTO "public"."auth_permission" VALUES (68, 'Can view Configuration système', 17, 'view_configurationsysteme');
INSERT INTO "public"."auth_permission" VALUES (69, 'Can add Statistique plateforme', 18, 'add_statistiquesplateforme');
INSERT INTO "public"."auth_permission" VALUES (70, 'Can change Statistique plateforme', 18, 'change_statistiquesplateforme');
INSERT INTO "public"."auth_permission" VALUES (71, 'Can delete Statistique plateforme', 18, 'delete_statistiquesplateforme');
INSERT INTO "public"."auth_permission" VALUES (72, 'Can view Statistique plateforme', 18, 'view_statistiquesplateforme');
INSERT INTO "public"."auth_permission" VALUES (73, 'Can add Vérification QR', 19, 'add_verificationqr');
INSERT INTO "public"."auth_permission" VALUES (74, 'Can change Vérification QR', 19, 'change_verificationqr');
INSERT INTO "public"."auth_permission" VALUES (75, 'Can delete Vérification QR', 19, 'delete_verificationqr');
INSERT INTO "public"."auth_permission" VALUES (76, 'Can view Vérification QR', 19, 'view_verificationqr');
INSERT INTO "public"."auth_permission" VALUES (77, 'Can add Profil administrateur', 20, 'add_adminuserprofile');
INSERT INTO "public"."auth_permission" VALUES (78, 'Can change Profil administrateur', 20, 'change_adminuserprofile');
INSERT INTO "public"."auth_permission" VALUES (79, 'Can delete Profil administrateur', 20, 'delete_adminuserprofile');
INSERT INTO "public"."auth_permission" VALUES (80, 'Can view Profil administrateur', 20, 'view_adminuserprofile');
INSERT INTO "public"."auth_permission" VALUES (81, 'Can add Version de données', 21, 'add_dataversion');
INSERT INTO "public"."auth_permission" VALUES (82, 'Can change Version de données', 21, 'change_dataversion');
INSERT INTO "public"."auth_permission" VALUES (83, 'Can delete Version de données', 21, 'delete_dataversion');
INSERT INTO "public"."auth_permission" VALUES (84, 'Can view Version de données', 21, 'view_dataversion');
INSERT INTO "public"."auth_permission" VALUES (85, 'Can add Session administrateur', 22, 'add_adminsession');
INSERT INTO "public"."auth_permission" VALUES (86, 'Can change Session administrateur', 22, 'change_adminsession');
INSERT INTO "public"."auth_permission" VALUES (87, 'Can delete Session administrateur', 22, 'delete_adminsession');
INSERT INTO "public"."auth_permission" VALUES (88, 'Can view Session administrateur', 22, 'view_adminsession');
INSERT INTO "public"."auth_permission" VALUES (89, 'Can add Groupe de permissions', 23, 'add_permissiongroup');
INSERT INTO "public"."auth_permission" VALUES (90, 'Can change Groupe de permissions', 23, 'change_permissiongroup');
INSERT INTO "public"."auth_permission" VALUES (91, 'Can delete Groupe de permissions', 23, 'delete_permissiongroup');
INSERT INTO "public"."auth_permission" VALUES (92, 'Can view Groupe de permissions', 23, 'view_permissiongroup');
INSERT INTO "public"."auth_permission" VALUES (93, 'Can add Profil entreprise', 24, 'add_companyprofile');
INSERT INTO "public"."auth_permission" VALUES (94, 'Can change Profil entreprise', 24, 'change_companyprofile');
INSERT INTO "public"."auth_permission" VALUES (95, 'Can delete Profil entreprise', 24, 'delete_companyprofile');
INSERT INTO "public"."auth_permission" VALUES (96, 'Can view Profil entreprise', 24, 'view_companyprofile');
INSERT INTO "public"."auth_permission" VALUES (97, 'Can add Profil service d''urgence', 25, 'add_emergencyserviceprofile');
INSERT INTO "public"."auth_permission" VALUES (98, 'Can change Profil service d''urgence', 25, 'change_emergencyserviceprofile');
INSERT INTO "public"."auth_permission" VALUES (99, 'Can delete Profil service d''urgence', 25, 'delete_emergencyserviceprofile');
INSERT INTO "public"."auth_permission" VALUES (100, 'Can view Profil service d''urgence', 25, 'view_emergencyserviceprofile');
INSERT INTO "public"."auth_permission" VALUES (101, 'Can add Profil administrateur gouvernemental', 26, 'add_governmentadminprofile');
INSERT INTO "public"."auth_permission" VALUES (102, 'Can change Profil administrateur gouvernemental', 26, 'change_governmentadminprofile');
INSERT INTO "public"."auth_permission" VALUES (103, 'Can delete Profil administrateur gouvernemental', 26, 'delete_governmentadminprofile');
INSERT INTO "public"."auth_permission" VALUES (104, 'Can view Profil administrateur gouvernemental', 26, 'view_governmentadminprofile');
INSERT INTO "public"."auth_permission" VALUES (105, 'Can add Profil individuel', 27, 'add_individualprofile');
INSERT INTO "public"."auth_permission" VALUES (106, 'Can change Profil individuel', 27, 'change_individualprofile');
INSERT INTO "public"."auth_permission" VALUES (107, 'Can delete Profil individuel', 27, 'delete_individualprofile');
INSERT INTO "public"."auth_permission" VALUES (108, 'Can view Profil individuel', 27, 'view_individualprofile');
INSERT INTO "public"."auth_permission" VALUES (109, 'Can add Profil forces de l''ordre', 28, 'add_lawenforcementprofile');
INSERT INTO "public"."auth_permission" VALUES (110, 'Can change Profil forces de l''ordre', 28, 'change_lawenforcementprofile');
INSERT INTO "public"."auth_permission" VALUES (111, 'Can delete Profil forces de l''ordre', 28, 'delete_lawenforcementprofile');
INSERT INTO "public"."auth_permission" VALUES (112, 'Can view Profil forces de l''ordre', 28, 'view_lawenforcementprofile');
INSERT INTO "public"."auth_permission" VALUES (113, 'Can add Document de vérification', 29, 'add_verificationdocument');
INSERT INTO "public"."auth_permission" VALUES (114, 'Can change Document de vérification', 29, 'change_verificationdocument');
INSERT INTO "public"."auth_permission" VALUES (115, 'Can delete Document de vérification', 29, 'delete_verificationdocument');
INSERT INTO "public"."auth_permission" VALUES (116, 'Can view Document de vérification', 29, 'view_verificationdocument');
INSERT INTO "public"."auth_permission" VALUES (117, 'Can add site', 30, 'add_site');
INSERT INTO "public"."auth_permission" VALUES (118, 'Can change site', 30, 'change_site');
INSERT INTO "public"."auth_permission" VALUES (119, 'Can delete site', 30, 'delete_site');
INSERT INTO "public"."auth_permission" VALUES (120, 'Can view site', 30, 'view_site');
INSERT INTO "public"."auth_permission" VALUES (121, 'Can add email address', 31, 'add_emailaddress');
INSERT INTO "public"."auth_permission" VALUES (122, 'Can change email address', 31, 'change_emailaddress');
INSERT INTO "public"."auth_permission" VALUES (123, 'Can delete email address', 31, 'delete_emailaddress');
INSERT INTO "public"."auth_permission" VALUES (124, 'Can view email address', 31, 'view_emailaddress');
INSERT INTO "public"."auth_permission" VALUES (125, 'Can add email confirmation', 32, 'add_emailconfirmation');
INSERT INTO "public"."auth_permission" VALUES (126, 'Can change email confirmation', 32, 'change_emailconfirmation');
INSERT INTO "public"."auth_permission" VALUES (127, 'Can delete email confirmation', 32, 'delete_emailconfirmation');
INSERT INTO "public"."auth_permission" VALUES (128, 'Can view email confirmation', 32, 'view_emailconfirmation');
INSERT INTO "public"."auth_permission" VALUES (129, 'Can add social account', 33, 'add_socialaccount');
INSERT INTO "public"."auth_permission" VALUES (130, 'Can change social account', 33, 'change_socialaccount');
INSERT INTO "public"."auth_permission" VALUES (131, 'Can delete social account', 33, 'delete_socialaccount');
INSERT INTO "public"."auth_permission" VALUES (132, 'Can view social account', 33, 'view_socialaccount');
INSERT INTO "public"."auth_permission" VALUES (133, 'Can add social application', 34, 'add_socialapp');
INSERT INTO "public"."auth_permission" VALUES (134, 'Can change social application', 34, 'change_socialapp');
INSERT INTO "public"."auth_permission" VALUES (135, 'Can delete social application', 34, 'delete_socialapp');
INSERT INTO "public"."auth_permission" VALUES (136, 'Can view social application', 34, 'view_socialapp');
INSERT INTO "public"."auth_permission" VALUES (137, 'Can add social application token', 35, 'add_socialtoken');
INSERT INTO "public"."auth_permission" VALUES (138, 'Can change social application token', 35, 'change_socialtoken');
INSERT INTO "public"."auth_permission" VALUES (139, 'Can delete social application token', 35, 'delete_socialtoken');
INSERT INTO "public"."auth_permission" VALUES (140, 'Can view social application token', 35, 'view_socialtoken');
INSERT INTO "public"."auth_permission" VALUES (141, 'Can add Type de véhicule', 36, 'add_vehicletype');
INSERT INTO "public"."auth_permission" VALUES (142, 'Can change Type de véhicule', 36, 'change_vehicletype');
INSERT INTO "public"."auth_permission" VALUES (143, 'Can delete Type de véhicule', 36, 'delete_vehicletype');
INSERT INTO "public"."auth_permission" VALUES (144, 'Can view Type de véhicule', 36, 'view_vehicletype');
INSERT INTO "public"."auth_permission" VALUES (145, 'Can add Événement Webhook Stripe', 37, 'add_stripewebhookevent');
INSERT INTO "public"."auth_permission" VALUES (146, 'Can change Événement Webhook Stripe', 37, 'change_stripewebhookevent');
INSERT INTO "public"."auth_permission" VALUES (147, 'Can delete Événement Webhook Stripe', 37, 'delete_stripewebhookevent');
INSERT INTO "public"."auth_permission" VALUES (148, 'Can view Événement Webhook Stripe', 37, 'view_stripewebhookevent');
INSERT INTO "public"."auth_permission" VALUES (149, 'Can add Stripe configuration', 38, 'add_stripeconfig');
INSERT INTO "public"."auth_permission" VALUES (150, 'Can change Stripe configuration', 38, 'change_stripeconfig');
INSERT INTO "public"."auth_permission" VALUES (151, 'Can delete Stripe configuration', 38, 'delete_stripeconfig');
INSERT INTO "public"."auth_permission" VALUES (152, 'Can view Stripe configuration', 38, 'view_stripeconfig');
INSERT INTO "public"."auth_permission" VALUES (153, 'Can add Document du véhicule', 39, 'add_documentvehicule');
INSERT INTO "public"."auth_permission" VALUES (154, 'Can change Document du véhicule', 39, 'change_documentvehicule');
INSERT INTO "public"."auth_permission" VALUES (155, 'Can delete Document du véhicule', 39, 'delete_documentvehicule');
INSERT INTO "public"."auth_permission" VALUES (156, 'Can view Document du véhicule', 39, 'view_documentvehicule');

-- ----------------------------
-- Table structure for auth_user
-- ----------------------------
DROP TABLE IF EXISTS "public"."auth_user";
CREATE TABLE "public"."auth_user" (
  "id" int4 NOT NULL GENERATED BY DEFAULT AS IDENTITY (
INCREMENT 1
MINVALUE  1
MAXVALUE 2147483647
START 1
CACHE 1
),
  "password" varchar(128) COLLATE "pg_catalog"."default" NOT NULL,
  "last_login" timestamptz(6),
  "is_superuser" bool NOT NULL,
  "username" varchar(150) COLLATE "pg_catalog"."default" NOT NULL,
  "first_name" varchar(150) COLLATE "pg_catalog"."default" NOT NULL,
  "last_name" varchar(150) COLLATE "pg_catalog"."default" NOT NULL,
  "email" varchar(254) COLLATE "pg_catalog"."default" NOT NULL,
  "is_staff" bool NOT NULL,
  "is_active" bool NOT NULL,
  "date_joined" timestamptz(6) NOT NULL
)
;

-- ----------------------------
-- Records of auth_user
-- ----------------------------
INSERT INTO "public"."auth_user" VALUES (1, '', NULL, 'f', 'test_user', 'Test', 'User', 'test@example.com', 'f', 't', '2025-11-01 06:36:50.149356+03');
INSERT INTO "public"."auth_user" VALUES (2, 'pbkdf2_sha256$1000000$D3Nx1wt45PbpKg4L1dUauE$7MBFo4dE/6qaOpzGc8TKuUaS4npjG4om+2SP5Eyvm3k=', NULL, 'f', 'fleet_test', '', '', 'fleet@test.com', 'f', 't', '2025-11-01 06:53:16.596189+03');
INSERT INTO "public"."auth_user" VALUES (4, 'pbkdf2_sha256$1000000$xgOuCS1Gcq4gSRZ51Z6ypj$sPP3xoKwvro/nO+stPl5mB2prinbsB+A5XlMPKFiYec=', NULL, 'f', 'testuser', '', '', 'test@example.com', 'f', 't', '2025-11-01 07:27:28.262514+03');
INSERT INTO "public"."auth_user" VALUES (7, 'pbkdf2_sha256$1000000$DOdEYzqtLQzCmzeNO5SIfO$i00E9vQrto5B4HXW4E9gSDh3X+Kgmmbl/zLVGdG9Kg4=', '2025-11-02 21:11:52.799863+03', 'f', 'extracom', 'extracom', 'digital', '', 'f', 't', '2025-11-02 19:51:28.082124+03');
INSERT INTO "public"."auth_user" VALUES (5, 'pbkdf2_sha256$1000000$VOPtEOyUp5ulchzLllbpYT$Pg2OJ2WreTUmB6n0f/OKR9zQf6QPEEMhvmX6ofOTKD0=', NULL, 't', 'rijas', '', '', '', 't', 't', '2025-11-01 15:05:39.764293+03');
INSERT INTO "public"."auth_user" VALUES (18, 'pbkdf2_sha256$1000000$L2HpyLvPhW25lRPsO5oV6I$1uep6KGJ1Oj5MlsuVe4QGFTpCsbHMpSbTJPcism9w4Q=', '2025-11-03 12:26:29.733318+03', 'f', 'extracom3', 'test', 'tst', '', 'f', 't', '2025-11-02 20:03:42.238677+03');
INSERT INTO "public"."auth_user" VALUES (19, 'pbkdf2_sha256$1000000$UiLa24fMIuHfJm9PAqNHxP$Ioc/szobMH4hEneAdu/cTPcOZ1EGFVnJqSCcstPfLPc=', '2025-11-04 11:27:52.400677+03', 'f', 'testuser1', 'Test', 'User', 'testuser1@example.com', 'f', 't', '2025-11-04 11:23:46.801414+03');
INSERT INTO "public"."auth_user" VALUES (3, 'pbkdf2_sha256$1000000$dTyVSeql4U83DdeTl9C5HM$iXpTUfteX6iOCHAAK4tEV9LNddQXSeoBMy6oxtFov3g=', '2025-11-01 21:14:59.171974+03', 'f', 'rijadts', '', '', '', 'f', 't', '2025-11-01 07:27:00.09392+03');
INSERT INTO "public"."auth_user" VALUES (8, 'pbkdf2_sha256$1000000$kK0V0zwP2yfVfp9CcafWyk$uLwe2pKo7h8ecw/V5xazi6NwTUlH+dmlHYuZt7HWYQU=', NULL, 'f', 'testcompany', 'Test', 'Company', 'test@company.com', 'f', 't', '2025-11-02 19:53:56.217201+03');
INSERT INTO "public"."auth_user" VALUES (9, 'pbkdf2_sha256$1000000$ivDNOJA6G7WwKXBbNSqhIf$pGCx7UE8R8BZOrzYoJ6b9ZVkUUInLszB8y5goa82MgM=', NULL, 'f', 'testcompany2', 'Test', 'Company2', 'test2@company.com', 'f', 't', '2025-11-02 19:55:00.620885+03');
INSERT INTO "public"."auth_user" VALUES (10, 'testpass', NULL, 'f', 'testsignal', '', '', '', 'f', 't', '2025-11-02 19:55:21.56874+03');
INSERT INTO "public"."auth_user" VALUES (11, 'testpass', NULL, 'f', 'testsignal2', '', '', '', 'f', 't', '2025-11-02 19:55:42.327405+03');
INSERT INTO "public"."auth_user" VALUES (12, 'testpass', NULL, 'f', 'testsignal3', '', '', '', 'f', 't', '2025-11-02 19:55:56.187054+03');
INSERT INTO "public"."auth_user" VALUES (13, 'testpass', NULL, 'f', 'testsignal4', '', '', '', 'f', 't', '2025-11-02 19:56:11.273587+03');
INSERT INTO "public"."auth_user" VALUES (14, 'testpass', NULL, 'f', 'testsignal5', '', '', '', 'f', 't', '2025-11-02 19:57:05.794566+03');
INSERT INTO "public"."auth_user" VALUES (16, 'testpass', NULL, 'f', 'testcompany3', '', '', '', 'f', 't', '2025-11-02 19:57:33.342222+03');
INSERT INTO "public"."auth_user" VALUES (17, 'pbkdf2_sha256$1000000$OnfXW252RcTSZToIOhnFOn$40VLBQR21zVc9Qp2IHY6YYW+RY23WsYXUZukpipPb4A=', NULL, 'f', 'testcompany4', 'Test', 'Company', 'test@company.com', 'f', 't', '2025-11-02 19:58:35.332423+03');
INSERT INTO "public"."auth_user" VALUES (6, 'pbkdf2_sha256$1000000$RZyS7dguOShxJJpphJ48wo$IOwQYP6LwMK6zGvJFvkvTwk13F+qvR3DsVDxliRhAGM=', '2025-11-02 20:44:53.392233+03', 't', 'admin', '', '', 'admin@admin.com', 't', 't', '2025-11-01 15:07:04.073938+03');

-- ----------------------------
-- Table structure for auth_user_groups
-- ----------------------------
DROP TABLE IF EXISTS "public"."auth_user_groups";
CREATE TABLE "public"."auth_user_groups" (
  "id" int8 NOT NULL GENERATED BY DEFAULT AS IDENTITY (
INCREMENT 1
MINVALUE  1
MAXVALUE 9223372036854775807
START 1
CACHE 1
),
  "user_id" int4 NOT NULL,
  "group_id" int4 NOT NULL
)
;

-- ----------------------------
-- Records of auth_user_groups
-- ----------------------------

-- ----------------------------
-- Table structure for auth_user_user_permissions
-- ----------------------------
DROP TABLE IF EXISTS "public"."auth_user_user_permissions";
CREATE TABLE "public"."auth_user_user_permissions" (
  "id" int8 NOT NULL GENERATED BY DEFAULT AS IDENTITY (
INCREMENT 1
MINVALUE  1
MAXVALUE 9223372036854775807
START 1
CACHE 1
),
  "user_id" int4 NOT NULL,
  "permission_id" int4 NOT NULL
)
;

-- ----------------------------
-- Records of auth_user_user_permissions
-- ----------------------------

-- ----------------------------
-- Table structure for core_auditlog
-- ----------------------------
DROP TABLE IF EXISTS "public"."core_auditlog";
CREATE TABLE "public"."core_auditlog" (
  "id" uuid NOT NULL,
  "action" varchar(50) COLLATE "pg_catalog"."default" NOT NULL,
  "table_concernee" varchar(50) COLLATE "pg_catalog"."default" NOT NULL,
  "objet_id" varchar(50) COLLATE "pg_catalog"."default" NOT NULL,
  "donnees_avant" jsonb,
  "donnees_apres" jsonb,
  "adresse_ip" inet,
  "user_agent" text COLLATE "pg_catalog"."default" NOT NULL,
  "session_id" varchar(100) COLLATE "pg_catalog"."default" NOT NULL,
  "date_action" timestamptz(6) NOT NULL,
  "user_id" int4
)
;

-- ----------------------------
-- Records of core_auditlog
-- ----------------------------

-- ----------------------------
-- Table structure for core_companyprofile
-- ----------------------------
DROP TABLE IF EXISTS "public"."core_companyprofile";
CREATE TABLE "public"."core_companyprofile" (
  "id" uuid NOT NULL,
  "company_name" varchar(200) COLLATE "pg_catalog"."default" NOT NULL,
  "tax_id" varchar(50) COLLATE "pg_catalog"."default" NOT NULL,
  "business_registration_number" varchar(50) COLLATE "pg_catalog"."default" NOT NULL,
  "industry_sector" varchar(100) COLLATE "pg_catalog"."default" NOT NULL,
  "fleet_size" int4 NOT NULL,
  "address" text COLLATE "pg_catalog"."default" NOT NULL,
  "created_at" timestamptz(6) NOT NULL,
  "user_profile_id" uuid NOT NULL
)
;

-- ----------------------------
-- Records of core_companyprofile
-- ----------------------------

-- ----------------------------
-- Table structure for core_emergencyserviceprofile
-- ----------------------------
DROP TABLE IF EXISTS "public"."core_emergencyserviceprofile";
CREATE TABLE "public"."core_emergencyserviceprofile" (
  "id" uuid NOT NULL,
  "organization_name" varchar(200) COLLATE "pg_catalog"."default" NOT NULL,
  "service_type" varchar(50) COLLATE "pg_catalog"."default" NOT NULL,
  "official_license" varchar(100) COLLATE "pg_catalog"."default" NOT NULL,
  "department_contact" varchar(100) COLLATE "pg_catalog"."default" NOT NULL,
  "verification_document_url" varchar(500) COLLATE "pg_catalog"."default" NOT NULL,
  "created_at" timestamptz(6) NOT NULL,
  "user_profile_id" uuid NOT NULL
)
;

-- ----------------------------
-- Records of core_emergencyserviceprofile
-- ----------------------------

-- ----------------------------
-- Table structure for core_entrepriseprofile
-- ----------------------------
DROP TABLE IF EXISTS "public"."core_entrepriseprofile";
CREATE TABLE "public"."core_entrepriseprofile" (
  "id" uuid NOT NULL,
  "nom_entreprise" varchar(200) COLLATE "pg_catalog"."default" NOT NULL,
  "numero_contribuable" varchar(50) COLLATE "pg_catalog"."default" NOT NULL,
  "adresse" text COLLATE "pg_catalog"."default" NOT NULL,
  "contact_principal" varchar(100) COLLATE "pg_catalog"."default" NOT NULL,
  "secteur_activite" varchar(100) COLLATE "pg_catalog"."default" NOT NULL,
  "created_at" timestamptz(6) NOT NULL,
  "updated_at" timestamptz(6) NOT NULL,
  "user_id" int4 NOT NULL
)
;

-- ----------------------------
-- Records of core_entrepriseprofile
-- ----------------------------

-- ----------------------------
-- Table structure for core_governmentadminprofile
-- ----------------------------
DROP TABLE IF EXISTS "public"."core_governmentadminprofile";
CREATE TABLE "public"."core_governmentadminprofile" (
  "id" uuid NOT NULL,
  "department" varchar(100) COLLATE "pg_catalog"."default" NOT NULL,
  "position" varchar(100) COLLATE "pg_catalog"."default" NOT NULL,
  "employee_id" varchar(50) COLLATE "pg_catalog"."default" NOT NULL,
  "access_level" int4 NOT NULL,
  "created_at" timestamptz(6) NOT NULL,
  "user_profile_id" uuid NOT NULL
)
;

-- ----------------------------
-- Records of core_governmentadminprofile
-- ----------------------------

-- ----------------------------
-- Table structure for core_individualprofile
-- ----------------------------
DROP TABLE IF EXISTS "public"."core_individualprofile";
CREATE TABLE "public"."core_individualprofile" (
  "id" uuid NOT NULL,
  "identity_number" varchar(50) COLLATE "pg_catalog"."default" NOT NULL,
  "date_of_birth" date,
  "address" text COLLATE "pg_catalog"."default" NOT NULL,
  "emergency_contact" varchar(100) COLLATE "pg_catalog"."default" NOT NULL,
  "created_at" timestamptz(6) NOT NULL,
  "user_profile_id" uuid NOT NULL
)
;

-- ----------------------------
-- Records of core_individualprofile
-- ----------------------------

-- ----------------------------
-- Table structure for core_lawenforcementprofile
-- ----------------------------
DROP TABLE IF EXISTS "public"."core_lawenforcementprofile";
CREATE TABLE "public"."core_lawenforcementprofile" (
  "id" uuid NOT NULL,
  "badge_number" varchar(50) COLLATE "pg_catalog"."default" NOT NULL,
  "department" varchar(100) COLLATE "pg_catalog"."default" NOT NULL,
  "rank" varchar(50) COLLATE "pg_catalog"."default" NOT NULL,
  "jurisdiction" varchar(100) COLLATE "pg_catalog"."default" NOT NULL,
  "created_at" timestamptz(6) NOT NULL,
  "user_profile_id" uuid NOT NULL
)
;

-- ----------------------------
-- Records of core_lawenforcementprofile
-- ----------------------------

-- ----------------------------
-- Table structure for core_userprofile
-- ----------------------------
DROP TABLE IF EXISTS "public"."core_userprofile";
CREATE TABLE "public"."core_userprofile" (
  "id" uuid NOT NULL,
  "telephone" varchar(20) COLLATE "pg_catalog"."default" NOT NULL,
  "est_entreprise" bool NOT NULL,
  "langue_preferee" varchar(5) COLLATE "pg_catalog"."default" NOT NULL,
  "created_at" timestamptz(6) NOT NULL,
  "updated_at" timestamptz(6) NOT NULL,
  "user_id" int4 NOT NULL,
  "user_type" varchar(20) COLLATE "pg_catalog"."default" NOT NULL,
  "verification_status" varchar(20) COLLATE "pg_catalog"."default" NOT NULL
)
;

-- ----------------------------
-- Records of core_userprofile
-- ----------------------------
INSERT INTO "public"."core_userprofile" VALUES ('ad8a3af2-6a23-406e-9c86-3a3cbcbd2b3d', '+261330000000', 'f', 'fr', '2025-11-02 19:24:19.606902+03', '2025-11-02 19:24:19.606921+03', 6, 'government', 'verified');
INSERT INTO "public"."core_userprofile" VALUES ('ec996ead-07b4-4bf4-b914-792e4f2c9b16', '', 't', 'fr', '2025-11-02 19:51:29.144315+03', '2025-11-02 19:51:29.144326+03', 7, 'company', 'pending');
INSERT INTO "public"."core_userprofile" VALUES ('5ae9554f-f396-4feb-86a4-1980ff8700c3', '', 't', 'fr', '2025-11-02 19:53:57.492537+03', '2025-11-02 19:53:57.492549+03', 8, 'company', 'pending');
INSERT INTO "public"."core_userprofile" VALUES ('02191fae-fed9-41f0-abc9-9eb69c44e268', '', 't', 'fr', '2025-11-02 19:55:01.759969+03', '2025-11-02 19:55:01.75998+03', 9, 'company', 'pending');
INSERT INTO "public"."core_userprofile" VALUES ('51ae6e7e-ac48-4e68-9b57-076023ee0822', '', 'f', 'fr', '2025-11-02 19:55:21.651004+03', '2025-11-02 19:55:21.651019+03', 10, 'individual', 'pending');
INSERT INTO "public"."core_userprofile" VALUES ('0c868abe-53cb-4a47-ac90-71adb02aac06', '', 'f', 'fr', '2025-11-02 19:55:42.386683+03', '2025-11-02 19:55:42.386694+03', 11, 'individual', 'pending');
INSERT INTO "public"."core_userprofile" VALUES ('a355d73b-dcb0-4f53-8312-4e445776ff43', '', 'f', 'fr', '2025-11-02 19:55:56.406312+03', '2025-11-02 19:55:56.406331+03', 12, 'individual', 'pending');
INSERT INTO "public"."core_userprofile" VALUES ('26b2863e-4c0e-48f9-b32e-e07788b061a6', '', 'f', 'fr', '2025-11-02 19:56:11.341295+03', '2025-11-02 19:56:11.341307+03', 13, 'individual', 'pending');
INSERT INTO "public"."core_userprofile" VALUES ('7f158a24-7b04-467d-9d7f-db54d528d807', '', 'f', 'fr', '2025-11-02 19:57:05.896508+03', '2025-11-02 19:57:05.896522+03', 14, 'individual', 'pending');
INSERT INTO "public"."core_userprofile" VALUES ('2de0af72-f5e6-49d1-82ec-02f3977d8aed', '', 'f', 'fr', '2025-11-02 19:57:33.43735+03', '2025-11-02 19:57:33.437367+03', 16, 'individual', 'pending');
INSERT INTO "public"."core_userprofile" VALUES ('27f49bf5-20da-4823-98e4-da2b9f7fdf66', '', 't', 'fr', '2025-11-02 19:58:36.784137+03', '2025-11-02 19:58:36.78415+03', 17, 'company', 'pending');
INSERT INTO "public"."core_userprofile" VALUES ('477c0bc7-fce3-4851-8c51-60e86f4d8357', '', 't', 'fr', '2025-11-02 20:03:43.197044+03', '2025-11-02 20:03:43.197054+03', 18, 'company', 'pending');
INSERT INTO "public"."core_userprofile" VALUES ('fdf487f8-22b5-466e-bb3b-e5f8b602bcaa', '', 'f', 'fr', '2025-11-04 11:23:46.891929+03', '2025-11-04 11:24:37.792922+03', 19, 'individual', 'pending');

-- ----------------------------
-- Table structure for core_verificationdocument
-- ----------------------------
DROP TABLE IF EXISTS "public"."core_verificationdocument";
CREATE TABLE "public"."core_verificationdocument" (
  "id" uuid NOT NULL,
  "document_type" varchar(50) COLLATE "pg_catalog"."default" NOT NULL,
  "file_url" varchar(500) COLLATE "pg_catalog"."default" NOT NULL,
  "verification_status" varchar(20) COLLATE "pg_catalog"."default" NOT NULL,
  "verified_at" timestamptz(6),
  "uploaded_at" timestamptz(6) NOT NULL,
  "user_profile_id" uuid NOT NULL,
  "verified_by_id" int4
)
;

-- ----------------------------
-- Records of core_verificationdocument
-- ----------------------------

-- ----------------------------
-- Table structure for django_admin_log
-- ----------------------------
DROP TABLE IF EXISTS "public"."django_admin_log";
CREATE TABLE "public"."django_admin_log" (
  "id" int4 NOT NULL GENERATED BY DEFAULT AS IDENTITY (
INCREMENT 1
MINVALUE  1
MAXVALUE 2147483647
START 1
CACHE 1
),
  "action_time" timestamptz(6) NOT NULL,
  "object_id" text COLLATE "pg_catalog"."default",
  "object_repr" varchar(200) COLLATE "pg_catalog"."default" NOT NULL,
  "action_flag" int2 NOT NULL,
  "change_message" text COLLATE "pg_catalog"."default" NOT NULL,
  "content_type_id" int4,
  "user_id" int4 NOT NULL
)
;

-- ----------------------------
-- Records of django_admin_log
-- ----------------------------

-- ----------------------------
-- Table structure for django_content_type
-- ----------------------------
DROP TABLE IF EXISTS "public"."django_content_type";
CREATE TABLE "public"."django_content_type" (
  "id" int4 NOT NULL GENERATED BY DEFAULT AS IDENTITY (
INCREMENT 1
MINVALUE  1
MAXVALUE 2147483647
START 1
CACHE 1
),
  "app_label" varchar(100) COLLATE "pg_catalog"."default" NOT NULL,
  "model" varchar(100) COLLATE "pg_catalog"."default" NOT NULL
)
;

-- ----------------------------
-- Records of django_content_type
-- ----------------------------
INSERT INTO "public"."django_content_type" VALUES (1, 'admin', 'logentry');
INSERT INTO "public"."django_content_type" VALUES (2, 'auth', 'permission');
INSERT INTO "public"."django_content_type" VALUES (3, 'auth', 'group');
INSERT INTO "public"."django_content_type" VALUES (4, 'auth', 'user');
INSERT INTO "public"."django_content_type" VALUES (5, 'contenttypes', 'contenttype');
INSERT INTO "public"."django_content_type" VALUES (6, 'sessions', 'session');
INSERT INTO "public"."django_content_type" VALUES (7, 'core', 'auditlog');
INSERT INTO "public"."django_content_type" VALUES (8, 'core', 'entrepriseprofile');
INSERT INTO "public"."django_content_type" VALUES (9, 'core', 'userprofile');
INSERT INTO "public"."django_content_type" VALUES (10, 'vehicles', 'grilletarifaire');
INSERT INTO "public"."django_content_type" VALUES (11, 'vehicles', 'vehicule');
INSERT INTO "public"."django_content_type" VALUES (12, 'payments', 'paiementtaxe');
INSERT INTO "public"."django_content_type" VALUES (13, 'payments', 'qrcode');
INSERT INTO "public"."django_content_type" VALUES (14, 'notifications', 'notificationtemplate');
INSERT INTO "public"."django_content_type" VALUES (15, 'notifications', 'notification');
INSERT INTO "public"."django_content_type" VALUES (16, 'administration', 'agentverification');
INSERT INTO "public"."django_content_type" VALUES (17, 'administration', 'configurationsysteme');
INSERT INTO "public"."django_content_type" VALUES (18, 'administration', 'statistiquesplateforme');
INSERT INTO "public"."django_content_type" VALUES (19, 'administration', 'verificationqr');
INSERT INTO "public"."django_content_type" VALUES (20, 'administration', 'adminuserprofile');
INSERT INTO "public"."django_content_type" VALUES (21, 'administration', 'dataversion');
INSERT INTO "public"."django_content_type" VALUES (22, 'administration', 'adminsession');
INSERT INTO "public"."django_content_type" VALUES (23, 'administration', 'permissiongroup');
INSERT INTO "public"."django_content_type" VALUES (24, 'core', 'companyprofile');
INSERT INTO "public"."django_content_type" VALUES (25, 'core', 'emergencyserviceprofile');
INSERT INTO "public"."django_content_type" VALUES (26, 'core', 'governmentadminprofile');
INSERT INTO "public"."django_content_type" VALUES (27, 'core', 'individualprofile');
INSERT INTO "public"."django_content_type" VALUES (28, 'core', 'lawenforcementprofile');
INSERT INTO "public"."django_content_type" VALUES (29, 'core', 'verificationdocument');
INSERT INTO "public"."django_content_type" VALUES (30, 'sites', 'site');
INSERT INTO "public"."django_content_type" VALUES (31, 'account', 'emailaddress');
INSERT INTO "public"."django_content_type" VALUES (32, 'account', 'emailconfirmation');
INSERT INTO "public"."django_content_type" VALUES (33, 'socialaccount', 'socialaccount');
INSERT INTO "public"."django_content_type" VALUES (34, 'socialaccount', 'socialapp');
INSERT INTO "public"."django_content_type" VALUES (35, 'socialaccount', 'socialtoken');
INSERT INTO "public"."django_content_type" VALUES (36, 'vehicles', 'vehicletype');
INSERT INTO "public"."django_content_type" VALUES (37, 'payments', 'stripewebhookevent');
INSERT INTO "public"."django_content_type" VALUES (38, 'payments', 'stripeconfig');
INSERT INTO "public"."django_content_type" VALUES (39, 'vehicles', 'documentvehicule');

-- ----------------------------
-- Table structure for django_migrations
-- ----------------------------
DROP TABLE IF EXISTS "public"."django_migrations";
CREATE TABLE "public"."django_migrations" (
  "id" int8 NOT NULL GENERATED BY DEFAULT AS IDENTITY (
INCREMENT 1
MINVALUE  1
MAXVALUE 9223372036854775807
START 1
CACHE 1
),
  "app" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "name" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "applied" timestamptz(6) NOT NULL
)
;

-- ----------------------------
-- Records of django_migrations
-- ----------------------------
INSERT INTO "public"."django_migrations" VALUES (1, 'contenttypes', '0001_initial', '2025-11-01 05:32:42.103465+03');
INSERT INTO "public"."django_migrations" VALUES (2, 'auth', '0001_initial', '2025-11-01 05:32:42.204897+03');
INSERT INTO "public"."django_migrations" VALUES (3, 'admin', '0001_initial', '2025-11-01 05:32:42.232474+03');
INSERT INTO "public"."django_migrations" VALUES (4, 'admin', '0002_logentry_remove_auto_add', '2025-11-01 05:32:42.241643+03');
INSERT INTO "public"."django_migrations" VALUES (5, 'admin', '0003_logentry_add_action_flag_choices', '2025-11-01 05:32:42.249472+03');
INSERT INTO "public"."django_migrations" VALUES (6, 'contenttypes', '0002_remove_content_type_name', '2025-11-01 05:32:42.273682+03');
INSERT INTO "public"."django_migrations" VALUES (7, 'auth', '0002_alter_permission_name_max_length', '2025-11-01 05:32:42.282538+03');
INSERT INTO "public"."django_migrations" VALUES (8, 'auth', '0003_alter_user_email_max_length', '2025-11-01 05:32:42.29247+03');
INSERT INTO "public"."django_migrations" VALUES (9, 'auth', '0004_alter_user_username_opts', '2025-11-01 05:32:42.300399+03');
INSERT INTO "public"."django_migrations" VALUES (10, 'auth', '0005_alter_user_last_login_null', '2025-11-01 05:32:42.309949+03');
INSERT INTO "public"."django_migrations" VALUES (11, 'auth', '0006_require_contenttypes_0002', '2025-11-01 05:32:42.311671+03');
INSERT INTO "public"."django_migrations" VALUES (12, 'auth', '0007_alter_validators_add_error_messages', '2025-11-01 05:32:42.320126+03');
INSERT INTO "public"."django_migrations" VALUES (13, 'auth', '0008_alter_user_username_max_length', '2025-11-01 05:32:42.336134+03');
INSERT INTO "public"."django_migrations" VALUES (14, 'auth', '0009_alter_user_last_name_max_length', '2025-11-01 05:32:42.345923+03');
INSERT INTO "public"."django_migrations" VALUES (15, 'auth', '0010_alter_group_name_max_length', '2025-11-01 05:32:42.356579+03');
INSERT INTO "public"."django_migrations" VALUES (16, 'auth', '0011_update_proxy_permissions', '2025-11-01 05:32:42.364389+03');
INSERT INTO "public"."django_migrations" VALUES (17, 'auth', '0012_alter_user_first_name_max_length', '2025-11-01 05:32:42.374907+03');
INSERT INTO "public"."django_migrations" VALUES (18, 'sessions', '0001_initial', '2025-11-01 05:32:42.387412+03');
INSERT INTO "public"."django_migrations" VALUES (19, 'vehicles', '0001_initial', '2025-11-01 05:42:29.55625+03');
INSERT INTO "public"."django_migrations" VALUES (20, 'payments', '0001_initial', '2025-11-01 05:42:29.627632+03');
INSERT INTO "public"."django_migrations" VALUES (21, 'administration', '0001_initial', '2025-11-01 05:42:29.817697+03');
INSERT INTO "public"."django_migrations" VALUES (22, 'core', '0001_initial', '2025-11-01 05:42:29.90451+03');
INSERT INTO "public"."django_migrations" VALUES (23, 'notifications', '0001_initial', '2025-11-01 05:42:29.956418+03');
INSERT INTO "public"."django_migrations" VALUES (24, 'notifications', '0002_notification_contenu_fr_notification_contenu_mg_and_more', '2025-11-01 05:44:40.839309+03');
INSERT INTO "public"."django_migrations" VALUES (25, 'vehicles', '0002_alter_vehicule_cylindree_cm3_and_more', '2025-11-01 08:08:31.280229+03');
INSERT INTO "public"."django_migrations" VALUES (26, 'administration', '0002_permissiongroup_adminsession_adminuserprofile_and_more', '2025-11-01 09:24:42.551575+03');
INSERT INTO "public"."django_migrations" VALUES (27, 'core', '0002_companyprofile_emergencyserviceprofile_and_more', '2025-11-01 15:06:09.595863+03');
INSERT INTO "public"."django_migrations" VALUES (28, 'notifications', '0003_remove_notification_contenu_fr_and_more', '2025-11-01 15:06:09.676794+03');
INSERT INTO "public"."django_migrations" VALUES (29, 'account', '0001_initial', '2025-11-01 17:51:38.887402+03');
INSERT INTO "public"."django_migrations" VALUES (30, 'account', '0002_email_max_length', '2025-11-01 17:51:39.002132+03');
INSERT INTO "public"."django_migrations" VALUES (31, 'account', '0003_alter_emailaddress_create_unique_verified_email', '2025-11-01 17:51:39.105793+03');
INSERT INTO "public"."django_migrations" VALUES (32, 'account', '0004_alter_emailaddress_drop_unique_email', '2025-11-01 17:51:39.224761+03');
INSERT INTO "public"."django_migrations" VALUES (33, 'account', '0005_emailaddress_idx_upper_email', '2025-11-01 17:51:39.288797+03');
INSERT INTO "public"."django_migrations" VALUES (34, 'account', '0006_emailaddress_lower', '2025-11-01 17:51:39.372434+03');
INSERT INTO "public"."django_migrations" VALUES (35, 'account', '0007_emailaddress_idx_email', '2025-11-01 17:51:39.477406+03');
INSERT INTO "public"."django_migrations" VALUES (36, 'account', '0008_emailaddress_unique_primary_email_fixup', '2025-11-01 17:51:39.553681+03');
INSERT INTO "public"."django_migrations" VALUES (37, 'account', '0009_emailaddress_unique_primary_email', '2025-11-01 17:51:39.599526+03');
INSERT INTO "public"."django_migrations" VALUES (38, 'sites', '0001_initial', '2025-11-01 17:51:39.609714+03');
INSERT INTO "public"."django_migrations" VALUES (39, 'sites', '0002_alter_domain_unique', '2025-11-01 17:51:39.626815+03');
INSERT INTO "public"."django_migrations" VALUES (40, 'socialaccount', '0001_initial', '2025-11-01 17:51:39.873979+03');
INSERT INTO "public"."django_migrations" VALUES (41, 'socialaccount', '0002_token_max_lengths', '2025-11-01 17:51:39.947861+03');
INSERT INTO "public"."django_migrations" VALUES (42, 'socialaccount', '0003_extra_data_default_dict', '2025-11-01 17:51:40.023986+03');
INSERT INTO "public"."django_migrations" VALUES (43, 'socialaccount', '0004_app_provider_id_settings', '2025-11-01 17:51:40.110005+03');
INSERT INTO "public"."django_migrations" VALUES (44, 'socialaccount', '0005_socialtoken_nullable_app', '2025-11-01 17:51:40.194338+03');
INSERT INTO "public"."django_migrations" VALUES (45, 'socialaccount', '0006_alter_socialaccount_extra_data', '2025-11-01 17:51:40.260063+03');
INSERT INTO "public"."django_migrations" VALUES (46, 'vehicles', '0003_update_vehicle_type_choices', '2025-11-02 16:49:52.037031+03');
INSERT INTO "public"."django_migrations" VALUES (47, 'vehicles', '0004_vehicletype_and_more', '2025-11-02 16:59:21.924262+03');
INSERT INTO "public"."django_migrations" VALUES (48, 'vehicles', '0005_auto_20251102_1658', '2025-11-02 16:59:22.012454+03');
INSERT INTO "public"."django_migrations" VALUES (49, 'payments', '0002_stripewebhookevent_paiementtaxe_amount_stripe_and_more', '2025-11-04 05:09:50.366318+03');
INSERT INTO "public"."django_migrations" VALUES (50, 'payments', '0003_stripeconfig', '2025-11-04 05:24:18.107946+03');
INSERT INTO "public"."django_migrations" VALUES (51, 'vehicles', '0006_documentvehicule', '2025-11-04 09:11:18.493946+03');

-- ----------------------------
-- Table structure for django_session
-- ----------------------------
DROP TABLE IF EXISTS "public"."django_session";
CREATE TABLE "public"."django_session" (
  "session_key" varchar(40) COLLATE "pg_catalog"."default" NOT NULL,
  "session_data" text COLLATE "pg_catalog"."default" NOT NULL,
  "expire_date" timestamptz(6) NOT NULL
)
;

-- ----------------------------
-- Records of django_session
-- ----------------------------
INSERT INTO "public"."django_session" VALUES ('tfocndg7dazlzbuc9fjtsgsph6pmng0a', '.eJxVjMEOwiAQRP-FsyEBlkI9evcbyO6ylaqhSWlPjf9um_Sgx5n3ZjaVcF1KWpvMaczqqpy6_HaE_JJ6gPzE-pg0T3WZR9KHok_a9H3K8r6d7t9BwVb2NXnf95aAECN3POwBXWRDEATI-A5McGxliIZ8BitBGAAhQIjshdTnC-puOA4:1vF3Cf:xYBzdm2rrhJPMBvqQ7MYN-YMkIw0qt58UpztUOgqfHU', '2025-11-01 08:27:01.049904+03');
INSERT INTO "public"."django_session" VALUES ('gikz2prlxv4x3pp4cjfjerd0bgdtzdf4', '.eJxVjMEOwiAQRP-FsyEBlkI9evcbyO6ylaqhSWlPjf9um_Sgx5n3ZjaVcF1KWpvMaczqqpy6_HaE_JJ6gPzE-pg0T3WZR9KHok_a9H3K8r6d7t9BwVb2NXnf95aAECN3POwBXWRDEATI-A5McGxliIZ8BitBGAAhQIjshdTnC-puOA4:1vF3Lu:1hEpnyJvFn1uHFHx-z-28dTZH2Te7A24ypP8pDrbmbc', '2025-11-01 08:36:34.076944+03');
INSERT INTO "public"."django_session" VALUES ('snpzx3sbglj2i9mj2gg15zkdar0plu07', '.eJxVjMEOwiAQRP-FsyEBlkI9evcbyO6ylaqhSWlPjf9um_Sgx5n3ZjaVcF1KWpvMaczqqpy6_HaE_JJ6gPzE-pg0T3WZR9KHok_a9H3K8r6d7t9BwVb2NXnf95aAECN3POwBXWRDEATI-A5McGxliIZ8BitBGAAhQIjshdTnC-puOA4:1vF3vW:Z-KHTkqwUvkGlnRqzg4mTffVRMCYXMAgWV-0vJZa70I', '2025-11-01 09:13:22.909358+03');
INSERT INTO "public"."django_session" VALUES ('586e6gmsos1jppc97u7ome4yw1di8475', '.eJxVjMEOwiAQRP-FsyEBlkI9evcbyO6ylaqhSWlPjf9um_Sgx5n3ZjaVcF1KWpvMaczqqpy6_HaE_JJ6gPzE-pg0T3WZR9KHok_a9H3K8r6d7t9BwVb2NXnf95aAECN3POwBXWRDEATI-A5McGxliIZ8BitBGAAhQIjshdTnC-puOA4:1vF3wy:iIbYkzlIkKgNBRQvzAZcPKQICv6LoEc6C-l-3VyXYe0', '2025-11-01 09:14:52.285451+03');
INSERT INTO "public"."django_session" VALUES ('6i7r98cov4w9md7s0ydz9vraz73e7h6s', '.eJxVjEsOwiAUAO_C2hCgPD4u3fcM5AEPqRqalHZlvLsh6UK3M5N5s4DHXsPRaQtLZldm2OWXRUxPakPkB7b7ytPa9m2JfCT8tJ3Pa6bX7Wz_BhV7HVvjLIEvXhmNk9JQyLpk0YOHqI2nKMhb4SBGgTQhSFVIZClJCAmY2ecLzJ43gA:1vFAOS:9pzah2Fygrg-WqnNRwsQfeJoujbyZ1vGR4xFs3vMbt8', '2025-11-01 16:07:40.558008+03');
INSERT INTO "public"."django_session" VALUES ('6fxxa88aj1y0w2zb10jme72wqhs3h5jl', '.eJxVjEsOwiAUAO_C2hCgPD4u3fcM5AEPqRqalHZlvLsh6UK3M5N5s4DHXsPRaQtLZldm2OWXRUxPakPkB7b7ytPa9m2JfCT8tJ3Pa6bX7Wz_BhV7HVvjLIEvXhmNk9JQyLpk0YOHqI2nKMhb4SBGgTQhSFVIZClJCAmY2ecLzJ43gA:1vFAOo:WRRPoLY16w2fL8uMpGLjnMmXDArpXYqWMctkBvl-B8I', '2025-11-01 16:08:02.433478+03');
INSERT INTO "public"."django_session" VALUES ('8xpb32x5g1eixr082ent5kwhg25ghqfn', '.eJxVjEsOwiAUAO_C2hCgPD4u3fcM5AEPqRqalHZlvLsh6UK3M5N5s4DHXsPRaQtLZldm2OWXRUxPakPkB7b7ytPa9m2JfCT8tJ3Pa6bX7Wz_BhV7HVvjLIEvXhmNk9JQyLpk0YOHqI2nKMhb4SBGgTQhSFVIZClJCAmY2ecLzJ43gA:1vFCMs:S54do3KydGJUi5bRpuQLCR1w2WGJJTYkg5kkSexwdLk', '2025-11-01 18:14:10.829107+03');
INSERT INTO "public"."django_session" VALUES ('bbyhptzzor5o28ktaes6je7pxkp8ik15', '.eJxVjEsOwiAUAO_C2hCgPD4u3fcM5AEPqRqalHZlvLsh6UK3M5N5s4DHXsPRaQtLZldm2OWXRUxPakPkB7b7ytPa9m2JfCT8tJ3Pa6bX7Wz_BhV7HVvjLIEvXhmNk9JQyLpk0YOHqI2nKMhb4SBGgTQhSFVIZClJCAmY2ecLzJ43gA:1vFDMl:No8X40eBdnmuj1TPcwwofn_1nre9p4BU3MM30cVWooA', '2025-11-01 19:18:07.438635+03');
INSERT INTO "public"."django_session" VALUES ('pvl9dnlzliekwntnun0qcw02z7ip6d6g', '.eJxVjEsOwiAUAO_C2hCgPD4u3fcM5AEPqRqalHZlvLsh6UK3M5N5s4DHXsPRaQtLZldm2OWXRUxPakPkB7b7ytPa9m2JfCT8tJ3Pa6bX7Wz_BhV7HVvjLIEvXhmNk9JQyLpk0YOHqI2nKMhb4SBGgTQhSFVIZClJCAmY2ecLzJ43gA:1vFDZv:5WUcKWvl8rXC0KvxeGvS-zdgeswsfqHQO9ZjrJdeUXk', '2025-11-01 19:31:43.486954+03');
INSERT INTO "public"."django_session" VALUES ('rb9qa2r0q4tsjr6qr0iu85wfryi7x0bv', '.eJxVjEsOwiAUAO_C2hCgPD4u3fcM5AEPqRqalHZlvLsh6UK3M5N5s4DHXsPRaQtLZldm2OWXRUxPakPkB7b7ytPa9m2JfCT8tJ3Pa6bX7Wz_BhV7HVvjLIEvXhmNk9JQyLpk0YOHqI2nKMhb4SBGgTQhSFVIZClJCAmY2ecLzJ43gA:1vFEgK:BS48n3YU-3oBItkqTRlfXbwfsaKPeG0-7VTA2L1EMN8', '2025-11-01 20:42:24.886049+03');
INSERT INTO "public"."django_session" VALUES ('1uruo96rngde1nanuqchff8ol8a4lfsk', '.eJxVjEsOwiAUAO_C2hCgPD4u3fcM5AEPqRqalHZlvLsh6UK3M5N5s4DHXsPRaQtLZldm2OWXRUxPakPkB7b7ytPa9m2JfCT8tJ3Pa6bX7Wz_BhV7HVvjLIEvXhmNk9JQyLpk0YOHqI2nKMhb4SBGgTQhSFVIZClJCAmY2ecLzJ43gA:1vFEx5:0lB-U9YliPsmJMEdbOGqC4R3I1ByLL-fdW2Ukt2O1YE', '2025-11-01 20:59:43.847085+03');
INSERT INTO "public"."django_session" VALUES ('jxdybmeyzk1qpfyag0a0s6sbnwo7f697', '.eJxVjMEOwiAQRP-FsyEBlkI9evcbyO6ylaqhSWlPjf9um_Sgx5n3ZjaVcF1KWpvMaczqqpy6_HaE_JJ6gPzE-pg0T3WZR9KHok_a9H3K8r6d7t9BwVb2NXnf95aAECN3POwBXWRDEATI-A5McGxliIZ8BitBGAAhQIjshdTnC-puOA4:1vFG7v:KVyBHcYF12faTMLXEWWK4xncpzJwOkwoWirCeNsz_mc', '2025-11-01 22:14:59.179577+03');
INSERT INTO "public"."django_session" VALUES ('q609z4tx6tjh4m6c6p05sl54j0okc2q0', '.eJxVjEsOwiAUAO_C2hCgPD4u3fcM5AEPqRqalHZlvLsh6UK3M5N5s4DHXsPRaQtLZldm2OWXRUxPakPkB7b7ytPa9m2JfCT8tJ3Pa6bX7Wz_BhV7HVvjLIEvXhmNk9JQyLpk0YOHqI2nKMhb4SBGgTQhSFVIZClJCAmY2ecLzJ43gA:1vFOAH:62tv7YjQnGZAuZmbS5rb1x8Ya5WAbvN-bJ5sqQn1_A4', '2025-11-02 06:49:57.572862+03');
INSERT INTO "public"."django_session" VALUES ('bgh0pugpmfeptesop2jzbnw3bijdlbdl', '.eJxVjEsOwiAUAO_C2hCgPD4u3fcM5AEPqRqalHZlvLsh6UK3M5N5s4DHXsPRaQtLZldm2OWXRUxPakPkB7b7ytPa9m2JfCT8tJ3Pa6bX7Wz_BhV7HVvjLIEvXhmNk9JQyLpk0YOHqI2nKMhb4SBGgTQhSFVIZClJCAmY2ecLzJ43gA:1vFOfG:YsAoHhJh5KI13Uwq8eRQqSueLCfUesdFu3XiPmWnpAM', '2025-11-02 07:21:58.696932+03');
INSERT INTO "public"."django_session" VALUES ('u371xw0lzfbnyxxyr13zwmodvxkw6njn', '.eJxVjEsOwiAUAO_C2hCgPD4u3fcM5AEPqRqalHZlvLsh6UK3M5N5s4DHXsPRaQtLZldm2OWXRUxPakPkB7b7ytPa9m2JfCT8tJ3Pa6bX7Wz_BhV7HVvjLIEvXhmNk9JQyLpk0YOHqI2nKMhb4SBGgTQhSFVIZClJCAmY2ecLzJ43gA:1vFOo0:sLkOWIpNzSPI-T9ld0tWG6hO1Yna5us8OQ4TWchxWas', '2025-11-02 07:31:00.283853+03');
INSERT INTO "public"."django_session" VALUES ('7tt8363g4l1h1v1eb1l6mjaqwgbx6s6s', '.eJxVjEsOwiAUAO_C2hCgPD4u3fcM5AEPqRqalHZlvLsh6UK3M5N5s4DHXsPRaQtLZldm2OWXRUxPakPkB7b7ytPa9m2JfCT8tJ3Pa6bX7Wz_BhV7HVvjLIEvXhmNk9JQyLpk0YOHqI2nKMhb4SBGgTQhSFVIZClJCAmY2ecLzJ43gA:1vFPym:NgdMaHUMdI3TmsswqV67qBXdBZg6tyYhLwg81PE2H6w', '2025-11-02 08:46:12.557752+03');
INSERT INTO "public"."django_session" VALUES ('35rllyt8i7nc2sqcmhoihrgjz7tg724p', '.eJxVjEsOwiAUAO_C2hCgPD4u3fcM5AEPqRqalHZlvLsh6UK3M5N5s4DHXsPRaQtLZldm2OWXRUxPakPkB7b7ytPa9m2JfCT8tJ3Pa6bX7Wz_BhV7HVvjLIEvXhmNk9JQyLpk0YOHqI2nKMhb4SBGgTQhSFVIZClJCAmY2ecLzJ43gA:1vFQ2R:GAtjYEIvWgLO5JSHHbyg-81Ts-TSX3QtUggCU5EbYQA', '2025-11-02 08:49:59.371677+03');
INSERT INTO "public"."django_session" VALUES ('63pujspx8rrtfwmjp4oczo8rydc8xnbt', '.eJxVjEsOwiAUAO_C2hCgPD4u3fcM5AEPqRqalHZlvLsh6UK3M5N5s4DHXsPRaQtLZldm2OWXRUxPakPkB7b7ytPa9m2JfCT8tJ3Pa6bX7Wz_BhV7HVvjLIEvXhmNk9JQyLpk0YOHqI2nKMhb4SBGgTQhSFVIZClJCAmY2ecLzJ43gA:1vFXfi:Wuu9MobKtQlmYADn_hPPspPfneLKh8XX-m5aJTf2y0U', '2025-11-02 16:59:02.166008+03');
INSERT INTO "public"."django_session" VALUES ('3klihswi6wuoiof8bfff0tyens0x1xgd', '.eJxVjEsOwiAUAO_C2hCgPD4u3fcM5AEPqRqalHZlvLsh6UK3M5N5s4DHXsPRaQtLZldm2OWXRUxPakPkB7b7ytPa9m2JfCT8tJ3Pa6bX7Wz_BhV7HVvjLIEvXhmNk9JQyLpk0YOHqI2nKMhb4SBGgTQhSFVIZClJCAmY2ecLzJ43gA:1vFYjO:6vAhnTm2IB2cbDN-DUOs-nKk_u-UgDw2TlKUkxzDy6M', '2025-11-02 18:06:54.657696+03');
INSERT INTO "public"."django_session" VALUES ('0uzk6j4yc52ld8ssmtx9ctz3t4dat0vq', '.eJxVjEsOwiAUAO_C2hCgPD4u3fcM5AEPqRqalHZlvLsh6UK3M5N5s4DHXsPRaQtLZldm2OWXRUxPakPkB7b7ytPa9m2JfCT8tJ3Pa6bX7Wz_BhV7HVvjLIEvXhmNk9JQyLpk0YOHqI2nKMhb4SBGgTQhSFVIZClJCAmY2ecLzJ43gA:1vFZiY:keuOPNPc2YyPVtXQ2uZkfq4rpCx90vEpkXXbrmb9ugU', '2025-11-02 19:10:06.114646+03');
INSERT INTO "public"."django_session" VALUES ('mv1os9oplcdnsdiy55gqnt4g7nd20lkb', '.eJxVjDsOwyAQRO9CHSGwYYGU6X0GtMsnOIlAMnYV5e6xJRdJNdK8N_NmHre1-K2nxc-RXRmwy29HGJ6pHiA-sN4bD62uy0z8UPhJO59aTK_b6f4dFOxlX2MWIykTRRq0tRZyHglg0MoELZMTWmogUC5TVNaioaSjs3IktycEyT5f1Ik3Zw:1vFat2:fXcrH_u2UYB3ZyMfHZuZFQd09OK9PGmqRGaXiXPgFpw', '2025-11-02 20:25:00.811572+03');
INSERT INTO "public"."django_session" VALUES ('4sveqpr6xjaogzima6xt42yipo8va5tp', '.eJxVjDsOwyAQRO9CHSGwYYGU6X0GtMsnOIlAMnYV5e6xJRdJNdK8N_NmHre1-K2nxc-RXRmwy29HGJ6pHiA-sN4bD62uy0z8UPhJO59aTK_b6f4dFOxlX2MWIykTRRq0tRZyHglg0MoELZMTWmogUC5TVNaioaSjs3IktycEyT5f1Ik3Zw:1vFatX:lTI8U8s_f7d3LghK9GzasIeSyZG4hew4GQAwVS1dDjA', '2025-11-02 20:25:31.609951+03');
INSERT INTO "public"."django_session" VALUES ('0gq5bw63cyx1mtom4t9xwrk6xlgbz24m', 'e30:1vFbIf:wgMmZDtt2Tmq-Dk7hTF-dmDWEjEkxaN0V08w1K0QaWE', '2025-11-02 20:51:29.150743+03');
INSERT INTO "public"."django_session" VALUES ('jrzr8oxt9hm9lybtbmkyfjomzcrgpyvg', '.eJxVjDsOwyAQRO9CHSGwYYGU6X0GtMsnOIlAMnYV5e6xJRdJNdK8N_NmHre1-K2nxc-RXRmwy29HGJ6pHiA-sN4bD62uy0z8UPhJO59aTK_b6f4dFOxlX2MWIykTRRq0tRZyHglg0MoELZMTWmogUC5TVNaioaSjs3IktycEyT5f1Ik3Zw:1vFc8L:AKIrs8krqQ8m1RfpUtUDhub3uLwwQibDJ97-D5fh5n8', '2025-11-02 21:44:53.416325+03');
INSERT INTO "public"."django_session" VALUES ('s3eudjqhg331s4qwzx3k5bvhnapcv5gc', '.eJxVjDsOwyAQBe9CHSEwH0PK9D4DWnYhOIlAMnYV5e4RkoukfTPz3izAsZdw9LSFldiVSccuv2MEfKY6CD2g3hvHVvdtjXwo_KSdL43S63a6fwcFehm1y8ZnQR7JgdFkBEwejZykyZAtolaSrJCgUpoBMqKiWSsfk7baWMc-XyXVOJw:1vFqpZ:yQ3lwElccJd7GijdRGbb5v5EySzDARs9AGcGUQ4SWhc', '2025-11-03 13:26:29.738015+03');
INSERT INTO "public"."django_session" VALUES ('sjubno5m78uj6x73cdsgb63x8iumhbhe', '.eJxVjEEOwiAQRe_C2hBmoAIu3fcMhDKDVA0kpV0Z765NutDtf-_9lwhxW0vYOi9hJnER4MXpd5xienDdCd1jvTWZWl2XeZK7Ig_a5diIn9fD_TsosZdvrTOSzypFYMqAlo3S2SFoAtAuD85i1IQKkj8nx2QQGTEP1mg0gE68PwWgNzs:1vGCLS:rmken5OybQabnHaRU5gB5L0b0C-E4UQ6INI1Kc97keY', '2025-11-04 12:24:50.752319+03');
INSERT INTO "public"."django_session" VALUES ('n67o0ux7fvp57al22l0kj0kugsazmsya', '.eJxVjEEOwiAQRe_C2hBmoAIu3fcMhDKDVA0kpV0Z765NutDtf-_9lwhxW0vYOi9hJnER4MXpd5xienDdCd1jvTWZWl2XeZK7Ig_a5diIn9fD_TsosZdvrTOSzypFYMqAlo3S2SFoAtAuD85i1IQKkj8nx2QQGTEP1mg0gE68PwWgNzs:1vGCOO:v6piRo-mCuEvkjHB9Pczenj5LAlsAMvfvGZDyWhje5w', '2025-11-04 12:27:52.416811+03');

-- ----------------------------
-- Table structure for django_site
-- ----------------------------
DROP TABLE IF EXISTS "public"."django_site";
CREATE TABLE "public"."django_site" (
  "id" int4 NOT NULL GENERATED BY DEFAULT AS IDENTITY (
INCREMENT 1
MINVALUE  1
MAXVALUE 2147483647
START 1
CACHE 1
),
  "domain" varchar(100) COLLATE "pg_catalog"."default" NOT NULL,
  "name" varchar(50) COLLATE "pg_catalog"."default" NOT NULL
)
;

-- ----------------------------
-- Records of django_site
-- ----------------------------
INSERT INTO "public"."django_site" VALUES (1, 'example.com', 'example.com');

-- ----------------------------
-- Table structure for notifications_notification
-- ----------------------------
DROP TABLE IF EXISTS "public"."notifications_notification";
CREATE TABLE "public"."notifications_notification" (
  "id" uuid NOT NULL,
  "type_notification" varchar(20) COLLATE "pg_catalog"."default" NOT NULL,
  "titre" varchar(200) COLLATE "pg_catalog"."default" NOT NULL,
  "contenu" text COLLATE "pg_catalog"."default" NOT NULL,
  "langue" varchar(5) COLLATE "pg_catalog"."default" NOT NULL,
  "est_lue" bool NOT NULL,
  "date_envoi" timestamptz(6) NOT NULL,
  "date_lecture" timestamptz(6),
  "metadata" jsonb NOT NULL,
  "user_id" int4 NOT NULL
)
;

-- ----------------------------
-- Records of notifications_notification
-- ----------------------------
INSERT INTO "public"."notifications_notification" VALUES ('145ede7a-149b-4ee7-9630-b024f3b51958', 'system', 'Bienvenue sur la plateforme!', 'Bienvenue admin! Votre compte a été créé avec succès. Vous pouvez maintenant commencer à utiliser la plateforme.', 'fr', 'f', '2025-11-01 15:07:04.790087+03', NULL, '{"event": "user_registration"}', 6);
INSERT INTO "public"."notifications_notification" VALUES ('548a3452-8a7f-4924-9208-f22b1c0251e2', 'system', 'Connexion réussie', 'Vous vous êtes connecté avec succès le 01/11/2025 à 12:07.', 'fr', 'f', '2025-11-01 15:07:40.553218+03', NULL, '{"event": "user_login", "login_time": "2025-11-01T12:07:40.552752+00:00"}', 6);
INSERT INTO "public"."notifications_notification" VALUES ('c5f14059-0682-4d5f-80ff-65054dc17876', 'system', 'Connexion réussie', 'Vous vous êtes connecté avec succès le 01/11/2025 à 12:08.', 'fr', 'f', '2025-11-01 15:08:02.430927+03', NULL, '{"event": "user_login", "login_time": "2025-11-01T12:08:02.430555+00:00"}', 6);
INSERT INTO "public"."notifications_notification" VALUES ('0baa70bf-9505-403a-98d3-12398aef8f66', 'system', 'Connexion réussie', 'Vous vous êtes connecté avec succès le 01/11/2025 à 14:14.', 'fr', 'f', '2025-11-01 17:14:10.782348+03', NULL, '{"event": "user_login", "login_time": "2025-11-01T14:14:10.781964+00:00"}', 6);
INSERT INTO "public"."notifications_notification" VALUES ('355c1429-c2cf-441c-bce5-fed0e294e8f6', 'system', 'Connexion réussie', 'Vous vous êtes connecté avec succès le 01/11/2025 à 15:18.', 'fr', 'f', '2025-11-01 18:18:07.430646+03', NULL, '{"event": "user_login", "login_time": "2025-11-01T15:18:07.429515+00:00"}', 6);
INSERT INTO "public"."notifications_notification" VALUES ('cc2df115-ccbf-4526-b4a2-e9fc4bb52f29', 'system', 'Connexion réussie', 'Vous vous êtes connecté avec succès le 01/11/2025 à 15:31.', 'fr', 'f', '2025-11-01 18:31:43.484567+03', NULL, '{"event": "user_login", "login_time": "2025-11-01T15:31:43.484217+00:00"}', 6);
INSERT INTO "public"."notifications_notification" VALUES ('676fea1d-653e-4e13-8bf0-c5a6e0d5d499', 'system', 'Connexion réussie', 'Vous vous êtes connecté avec succès le 01/11/2025 à 16:42.', 'fr', 'f', '2025-11-01 19:42:24.872838+03', NULL, '{"event": "user_login", "login_time": "2025-11-01T16:42:24.872509+00:00"}', 6);
INSERT INTO "public"."notifications_notification" VALUES ('7aceb43b-a495-4e6c-abce-79e2fef7089e', 'system', 'Connexion réussie', 'Vous vous êtes connecté avec succès le 01/11/2025 à 16:59.', 'fr', 'f', '2025-11-01 19:59:43.832419+03', NULL, '{"event": "user_login", "login_time": "2025-11-01T16:59:43.831735+00:00"}', 6);
INSERT INTO "public"."notifications_notification" VALUES ('f11f81f8-8f62-4964-8bfb-5e44d10ee39a', 'system', 'Connexion réussie', 'Vous vous êtes connecté avec succès le 01/11/2025 à 17:25.', 'fr', 'f', '2025-11-01 20:25:42.400052+03', NULL, '{"event": "user_login", "login_time": "2025-11-01T17:25:42.399719+00:00"}', 6);
INSERT INTO "public"."notifications_notification" VALUES ('d95c4bf5-a271-4abb-ba7e-0c40d2142a76', 'system', 'Connexion réussie', 'Vous vous êtes connecté avec succès le 01/11/2025 à 18:14.', 'fr', 'f', '2025-11-01 21:14:59.177142+03', NULL, '{"event": "user_login", "login_time": "2025-11-01T18:14:59.176820+00:00"}', 3);
INSERT INTO "public"."notifications_notification" VALUES ('e9ae9738-9211-4126-805b-fd99464b4c51', 'system', 'Déconnexion', 'Vous vous êtes déconnecté le 01/11/2025 à 18:19.', 'fr', 'f', '2025-11-01 21:19:07.196449+03', NULL, '{"event": "user_logout", "logout_time": "2025-11-01T18:19:07.196067+00:00"}', 6);
INSERT INTO "public"."notifications_notification" VALUES ('994285f7-568a-4e7d-ae79-5e644c17986a', 'system', 'Connexion réussie', 'Vous vous êtes connecté avec succès le 02/11/2025 à 02:49.', 'fr', 'f', '2025-11-02 05:49:57.546873+03', NULL, '{"event": "user_login", "login_time": "2025-11-02T02:49:57.546521+00:00"}', 6);
INSERT INTO "public"."notifications_notification" VALUES ('a9946a86-9677-483f-a0a3-ab08ca4a95ff', 'system', 'Connexion réussie', 'Vous vous êtes connecté avec succès le 02/11/2025 à 03:15.', 'fr', 'f', '2025-11-02 06:15:09.774561+03', NULL, '{"event": "user_login", "login_time": "2025-11-02T03:15:09.774239+00:00"}', 6);
INSERT INTO "public"."notifications_notification" VALUES ('895a4157-d78e-40c7-a4b7-f391d4eb3677', 'system', 'Déconnexion', 'Vous vous êtes déconnecté le 02/11/2025 à 03:16.', 'fr', 'f', '2025-11-02 06:16:44.896642+03', NULL, '{"event": "user_logout", "logout_time": "2025-11-02T03:16:44.896298+00:00"}', 6);
INSERT INTO "public"."notifications_notification" VALUES ('ff206a43-cfb9-4143-b0d9-6da7f9d2b2f1', 'system', 'Connexion réussie', 'Vous vous êtes connecté avec succès le 02/11/2025 à 03:17.', 'fr', 'f', '2025-11-02 06:17:25.026759+03', NULL, '{"event": "user_login", "login_time": "2025-11-02T03:17:25.026520+00:00"}', 6);
INSERT INTO "public"."notifications_notification" VALUES ('93c10713-392c-4cab-ae5d-3b13e91c05f1', 'system', 'Connexion réussie', 'Vous vous êtes connecté avec succès le 02/11/2025 à 03:21.', 'fr', 'f', '2025-11-02 06:21:58.694653+03', NULL, '{"event": "user_login", "login_time": "2025-11-02T03:21:58.694363+00:00"}', 6);
INSERT INTO "public"."notifications_notification" VALUES ('ba084d61-3496-423d-9e78-3e0fbc108628', 'system', 'Déconnexion', 'Vous vous êtes déconnecté le 02/11/2025 à 03:29.', 'fr', 'f', '2025-11-02 06:29:43.915821+03', NULL, '{"event": "user_logout", "logout_time": "2025-11-02T03:29:43.915445+00:00"}', 6);
INSERT INTO "public"."notifications_notification" VALUES ('66d55be7-3fb8-4241-b7a3-a92f6f52369f', 'system', 'Connexion réussie', 'Vous vous êtes connecté avec succès le 02/11/2025 à 03:31.', 'fr', 'f', '2025-11-02 06:31:00.281353+03', NULL, '{"event": "user_login", "login_time": "2025-11-02T03:31:00.281124+00:00"}', 6);
INSERT INTO "public"."notifications_notification" VALUES ('653c61af-d8ea-4e88-abbb-9efba6162d0a', 'system', 'Connexion réussie', 'Vous vous êtes connecté avec succès le 02/11/2025 à 04:28.', 'fr', 'f', '2025-11-02 07:28:54.52248+03', NULL, '{"event": "user_login", "login_time": "2025-11-02T04:28:54.522095+00:00"}', 6);
INSERT INTO "public"."notifications_notification" VALUES ('1cc9703a-fe2d-427b-9d06-38bf226a0da6', 'system', 'Déconnexion', 'Vous vous êtes déconnecté le 02/11/2025 à 04:29.', 'fr', 'f', '2025-11-02 07:29:10.129939+03', NULL, '{"event": "user_logout", "logout_time": "2025-11-02T04:29:10.129571+00:00"}', 6);
INSERT INTO "public"."notifications_notification" VALUES ('5c3b3537-3793-4ae0-9a0e-cbc99378bfde', 'system', 'Connexion réussie', 'Vous vous êtes connecté avec succès le 02/11/2025 à 04:46.', 'fr', 'f', '2025-11-02 07:46:12.55211+03', NULL, '{"event": "user_login", "login_time": "2025-11-02T04:46:12.551725+00:00"}', 6);
INSERT INTO "public"."notifications_notification" VALUES ('6472b3ad-2fb0-4860-ae4c-9a681f9fb465', 'system', 'Connexion réussie', 'Vous vous êtes connecté avec succès le 02/11/2025 à 04:49.', 'fr', 'f', '2025-11-02 07:49:59.368704+03', NULL, '{"event": "user_login", "login_time": "2025-11-02T04:49:59.368236+00:00"}', 6);
INSERT INTO "public"."notifications_notification" VALUES ('10d02f98-1277-434d-95f7-a9301a62c670', 'system', 'Connexion réussie', 'Vous vous êtes connecté avec succès le 02/11/2025 à 12:59.', 'fr', 'f', '2025-11-02 15:59:02.132855+03', NULL, '{"event": "user_login", "login_time": "2025-11-02T12:59:02.132070+00:00"}', 6);
INSERT INTO "public"."notifications_notification" VALUES ('56170729-5877-4a07-babb-6a515545567d', 'system', 'Connexion réussie', 'Vous vous êtes connecté avec succès le 02/11/2025 à 14:06.', 'fr', 'f', '2025-11-02 17:06:54.654382+03', NULL, '{"event": "user_login", "login_time": "2025-11-02T14:06:54.653834+00:00"}', 6);
INSERT INTO "public"."notifications_notification" VALUES ('67e7a998-d828-407f-bc35-4276791b8cb1', 'system', 'Connexion réussie', 'Vous vous êtes connecté avec succès le 02/11/2025 à 15:10.', 'fr', 'f', '2025-11-02 18:10:06.111491+03', NULL, '{"event": "user_login", "login_time": "2025-11-02T15:10:06.111128+00:00"}', 6);
INSERT INTO "public"."notifications_notification" VALUES ('3aca85b4-90d2-4e36-a576-987a5da49adf', 'system', 'Connexion réussie', 'Vous vous êtes connecté avec succès le 02/11/2025 à 16:25.', 'fr', 'f', '2025-11-02 19:25:00.78532+03', NULL, '{"event": "user_login", "login_time": "2025-11-02T16:25:00.784970+00:00"}', 6);
INSERT INTO "public"."notifications_notification" VALUES ('a9a25a26-be1f-489d-b51f-f9e83c4b9675', 'system', 'Connexion réussie', 'Vous vous êtes connecté avec succès le 02/11/2025 à 16:25.', 'fr', 'f', '2025-11-02 19:25:31.607088+03', NULL, '{"event": "user_login", "login_time": "2025-11-02T16:25:31.606829+00:00"}', 6);
INSERT INTO "public"."notifications_notification" VALUES ('eb225256-f9da-4692-9757-351b484b1596', 'system', 'Bienvenue sur la plateforme!', 'Bienvenue extracom digital! Votre compte a été créé avec succès. Vous pouvez maintenant commencer à utiliser la plateforme.', 'fr', 'f', '2025-11-02 19:51:29.146014+03', NULL, '{"event": "user_registration"}', 7);
INSERT INTO "public"."notifications_notification" VALUES ('1981aa69-1edb-4fc9-8ca5-a6f75ad7e654', 'system', 'Bienvenue sur la plateforme!', 'Bienvenue Test Company! Votre compte a été créé avec succès. Vous pouvez maintenant commencer à utiliser la plateforme.', 'fr', 'f', '2025-11-02 19:53:57.494153+03', NULL, '{"event": "user_registration"}', 8);
INSERT INTO "public"."notifications_notification" VALUES ('fd450749-fd30-4604-b66d-9dda124736ae', 'system', 'Bienvenue sur la plateforme!', 'Bienvenue Test Company2! Votre compte a été créé avec succès. Vous pouvez maintenant commencer à utiliser la plateforme.', 'fr', 'f', '2025-11-02 19:55:01.762996+03', NULL, '{"event": "user_registration"}', 9);
INSERT INTO "public"."notifications_notification" VALUES ('3356a759-36de-430b-960e-5f5d8a0d0cf4', 'system', 'Bienvenue sur la plateforme!', 'Bienvenue testsignal! Votre compte a été créé avec succès. Vous pouvez maintenant commencer à utiliser la plateforme.', 'fr', 'f', '2025-11-02 19:55:21.655922+03', NULL, '{"event": "user_registration"}', 10);
INSERT INTO "public"."notifications_notification" VALUES ('0eb85a3e-7bde-42aa-8af5-2243a46edc51', 'system', 'Bienvenue sur la plateforme!', 'Bienvenue testsignal2! Votre compte a été créé avec succès. Vous pouvez maintenant commencer à utiliser la plateforme.', 'fr', 'f', '2025-11-02 19:55:42.39123+03', NULL, '{"event": "user_registration"}', 11);
INSERT INTO "public"."notifications_notification" VALUES ('c34a1087-457f-4749-ba65-5195150af2c0', 'system', 'Bienvenue sur la plateforme!', 'Bienvenue testsignal3! Votre compte a été créé avec succès. Vous pouvez maintenant commencer à utiliser la plateforme.', 'fr', 'f', '2025-11-02 19:55:56.413767+03', NULL, '{"event": "user_registration"}', 12);
INSERT INTO "public"."notifications_notification" VALUES ('b5daf4c8-7a82-4eb7-9486-837361f0bd0d', 'system', 'Bienvenue sur la plateforme!', 'Bienvenue testsignal4! Votre compte a été créé avec succès. Vous pouvez maintenant commencer à utiliser la plateforme.', 'fr', 'f', '2025-11-02 19:56:11.346634+03', NULL, '{"event": "user_registration"}', 13);
INSERT INTO "public"."notifications_notification" VALUES ('4d98cbcd-2b21-49bf-a784-8a795b2ba708', 'system', 'Bienvenue sur la plateforme!', 'Bienvenue testsignal5! Votre compte a été créé avec succès. Vous pouvez maintenant commencer à utiliser la plateforme.', 'fr', 'f', '2025-11-02 19:57:05.900446+03', NULL, '{"event": "user_registration"}', 14);
INSERT INTO "public"."notifications_notification" VALUES ('99467fb2-711d-43dd-900e-424a08a26aa0', 'system', 'Bienvenue sur la plateforme!', 'Bienvenue testcompany3! Votre compte a été créé avec succès. Vous pouvez maintenant commencer à utiliser la plateforme.', 'fr', 'f', '2025-11-02 19:57:33.441246+03', NULL, '{"event": "user_registration"}', 16);
INSERT INTO "public"."notifications_notification" VALUES ('0e575680-a635-46c2-826c-493aebe100ac', 'system', 'Bienvenue sur la plateforme!', 'Bienvenue Test Company! Votre compte a été créé avec succès. Vous pouvez maintenant commencer à utiliser la plateforme.', 'fr', 'f', '2025-11-02 19:58:36.786148+03', NULL, '{"event": "user_registration"}', 17);
INSERT INTO "public"."notifications_notification" VALUES ('dbea359d-b975-4a3d-a546-c12555db4954', 'system', 'Bienvenue sur la plateforme!', 'Bienvenue test tst! Votre compte a été créé avec succès. Vous pouvez maintenant commencer à utiliser la plateforme.', 'fr', 'f', '2025-11-02 20:03:43.198448+03', NULL, '{"event": "user_registration"}', 18);
INSERT INTO "public"."notifications_notification" VALUES ('8e9421bb-ed41-4130-a552-7d42da4b031b', 'system', 'Connexion réussie', 'Vous vous êtes connecté avec succès le 02/11/2025 à 17:03.', 'fr', 'f', '2025-11-02 20:03:43.20802+03', NULL, '{"event": "user_login", "login_time": "2025-11-02T17:03:43.207813+00:00"}', 18);
INSERT INTO "public"."notifications_notification" VALUES ('5037e9cd-9440-47e3-a554-636742ca6b8e', 'system', 'Bienvenue sur la plateforme!', 'Bienvenue test tst! Votre compte a été créé avec succès. Vous pouvez maintenant commencer à utiliser la plateforme.', 'fr', 't', '2025-11-02 20:03:43.2089+03', '2025-11-02 20:06:36.243005+03', '{"event": "user_registration"}', 18);
INSERT INTO "public"."notifications_notification" VALUES ('2306bf0e-38d8-46c3-b2e0-1608fae04c18', 'system', 'Connexion réussie', 'Vous vous êtes connecté avec succès le 02/11/2025 à 17:44.', 'fr', 'f', '2025-11-02 20:44:53.402763+03', NULL, '{"event": "user_login", "login_time": "2025-11-02T17:44:53.402241+00:00"}', 6);
INSERT INTO "public"."notifications_notification" VALUES ('d16864b4-695c-4b9f-b2e8-663c44c69b05', 'system', 'Déconnexion', 'Vous vous êtes déconnecté le 02/11/2025 à 17:56.', 'fr', 'f', '2025-11-02 20:56:28.522824+03', NULL, '{"event": "user_logout", "logout_time": "2025-11-02T17:56:28.522456+00:00"}', 18);
INSERT INTO "public"."notifications_notification" VALUES ('1852c386-9ef0-40b1-9e05-2890e6c8640e', 'system', 'Connexion réussie', 'Vous vous êtes connecté avec succès le 02/11/2025 à 18:08.', 'fr', 'f', '2025-11-02 21:08:04.853813+03', NULL, '{"event": "user_login", "login_time": "2025-11-02T18:08:04.853491+00:00"}', 18);
INSERT INTO "public"."notifications_notification" VALUES ('1a731aa8-3f8f-4b1c-8178-8726e9629f73', 'system', 'Connexion réussie', 'Vous vous êtes connecté avec succès le 02/11/2025 à 18:08.', 'fr', 'f', '2025-11-02 21:08:04.8586+03', NULL, '{"event": "user_login", "login_time": "2025-11-02T18:08:04.858364+00:00"}', 18);
INSERT INTO "public"."notifications_notification" VALUES ('eaa47246-1fbe-4f84-bda0-fab033d81624', 'system', 'Déconnexion', 'Vous vous êtes déconnecté le 02/11/2025 à 18:09.', 'fr', 'f', '2025-11-02 21:09:55.289527+03', NULL, '{"event": "user_logout", "logout_time": "2025-11-02T18:09:55.289115+00:00"}', 18);
INSERT INTO "public"."notifications_notification" VALUES ('a654749c-c1a1-4cf4-99b6-ce33b64941a9', 'system', 'Connexion réussie', 'Vous vous êtes connecté avec succès le 02/11/2025 à 18:11.', 'fr', 'f', '2025-11-02 21:11:52.797428+03', NULL, '{"event": "user_login", "login_time": "2025-11-02T18:11:52.797096+00:00"}', 7);
INSERT INTO "public"."notifications_notification" VALUES ('7c928ef8-a68b-4fc1-ad1a-4023b9da9d42', 'system', 'Connexion réussie', 'Vous vous êtes connecté avec succès le 02/11/2025 à 18:11.', 'fr', 'f', '2025-11-02 21:11:52.802345+03', NULL, '{"event": "user_login", "login_time": "2025-11-02T18:11:52.802005+00:00"}', 7);
INSERT INTO "public"."notifications_notification" VALUES ('c937f816-6e53-444d-9544-641614ec61e0', 'system', 'Déconnexion', 'Vous vous êtes déconnecté le 02/11/2025 à 18:11.', 'fr', 'f', '2025-11-02 21:11:58.39312+03', NULL, '{"event": "user_logout", "logout_time": "2025-11-02T18:11:58.392862+00:00"}', 7);
INSERT INTO "public"."notifications_notification" VALUES ('44657274-98c7-4d1b-bbce-d93a668541b6', 'system', 'Connexion réussie', 'Vous vous êtes connecté avec succès le 02/11/2025 à 18:19.', 'fr', 'f', '2025-11-02 21:19:51.41975+03', NULL, '{"event": "user_login", "login_time": "2025-11-02T18:19:51.419292+00:00"}', 18);
INSERT INTO "public"."notifications_notification" VALUES ('4f2874f7-6750-4af7-b6b4-d070275eafa4', 'system', 'Connexion réussie', 'Vous vous êtes connecté avec succès le 02/11/2025 à 18:19.', 'fr', 'f', '2025-11-02 21:19:51.426088+03', NULL, '{"event": "user_login", "login_time": "2025-11-02T18:19:51.425838+00:00"}', 18);
INSERT INTO "public"."notifications_notification" VALUES ('e05f4650-78fb-4b41-a4b3-103913b75348', 'system', 'Déconnexion', 'Vous vous êtes déconnecté le 02/11/2025 à 18:34.', 'fr', 'f', '2025-11-02 21:34:58.364621+03', NULL, '{"event": "user_logout", "logout_time": "2025-11-02T18:34:58.363985+00:00"}', 18);
INSERT INTO "public"."notifications_notification" VALUES ('a757ae04-fa02-4331-b658-bbb45922fc8e', 'system', 'Connexion réussie', 'Vous vous êtes connecté avec succès le 03/11/2025 à 09:26.', 'fr', 'f', '2025-11-03 12:26:29.697818+03', NULL, '{"event": "user_login", "login_time": "2025-11-03T09:26:29.697124+00:00"}', 18);
INSERT INTO "public"."notifications_notification" VALUES ('35deb54a-8cb2-4777-b3c5-575f35660727', 'system', 'Connexion réussie', 'Vous vous êtes connecté avec succès le 03/11/2025 à 09:26.', 'fr', 'f', '2025-11-03 12:26:29.735402+03', NULL, '{"event": "user_login", "login_time": "2025-11-03T09:26:29.735116+00:00"}', 18);
INSERT INTO "public"."notifications_notification" VALUES ('7c71fe5a-e802-4303-8297-c96178fb83a7', 'system', 'Bienvenue sur la plateforme!', 'Bienvenue testuser1! Votre compte a été créé avec succès. Vous pouvez maintenant commencer à utiliser la plateforme.', 'fr', 'f', '2025-11-04 11:23:46.895876+03', NULL, '{"event": "user_registration"}', 19);
INSERT INTO "public"."notifications_notification" VALUES ('5e4d01ce-9752-4891-8852-00f6be9405dc', 'system', 'Connexion réussie', 'Vous vous êtes connecté avec succès le 04/11/2025 à 08:24.', 'fr', 'f', '2025-11-04 11:24:50.748001+03', NULL, '{"event": "user_login", "login_time": "2025-11-04T08:24:50.747222+00:00"}', 19);
INSERT INTO "public"."notifications_notification" VALUES ('e55be279-38ff-48b6-a6d1-ea171cdce45d', 'system', 'Connexion réussie', 'Vous vous êtes connecté avec succès le 04/11/2025 à 08:27.', 'fr', 'f', '2025-11-04 11:27:52.412404+03', NULL, '{"event": "user_login", "login_time": "2025-11-04T08:27:52.411693+00:00"}', 19);
INSERT INTO "public"."notifications_notification" VALUES ('1dc5d78e-1478-41ae-a7ce-4ea4c89a85ac', 'document_uploaded', 'Nouveau document pour votre véhicule', 'Le document Photo de la plaque a été ajouté pour le véhicule 1234 TAA.', 'fr', 'f', '2025-11-04 11:27:53.475482+03', NULL, '{"vehicule": "1234 TAA", "document_id": "f8b5849d-4f10-4f03-a115-b5eab1a8cf72"}', 19);

-- ----------------------------
-- Table structure for notifications_notificationtemplate
-- ----------------------------
DROP TABLE IF EXISTS "public"."notifications_notificationtemplate";
CREATE TABLE "public"."notifications_notificationtemplate" (
  "id" int8 NOT NULL GENERATED BY DEFAULT AS IDENTITY (
INCREMENT 1
MINVALUE  1
MAXVALUE 9223372036854775807
START 1
CACHE 1
),
  "nom" varchar(100) COLLATE "pg_catalog"."default" NOT NULL,
  "type_template" varchar(50) COLLATE "pg_catalog"."default" NOT NULL,
  "langue" varchar(5) COLLATE "pg_catalog"."default" NOT NULL,
  "sujet" varchar(200) COLLATE "pg_catalog"."default" NOT NULL,
  "contenu_html" text COLLATE "pg_catalog"."default" NOT NULL,
  "contenu_texte" text COLLATE "pg_catalog"."default" NOT NULL,
  "variables_disponibles" jsonb NOT NULL,
  "est_actif" bool NOT NULL,
  "created_at" timestamptz(6) NOT NULL,
  "updated_at" timestamptz(6) NOT NULL
)
;

-- ----------------------------
-- Records of notifications_notificationtemplate
-- ----------------------------

-- ----------------------------
-- Table structure for payments_paiementtaxe
-- ----------------------------
DROP TABLE IF EXISTS "public"."payments_paiementtaxe";
CREATE TABLE "public"."payments_paiementtaxe" (
  "id" uuid NOT NULL,
  "annee_fiscale" int4 NOT NULL,
  "montant_du_ariary" numeric(12,2) NOT NULL,
  "montant_paye_ariary" numeric(12,2),
  "date_paiement" timestamptz(6),
  "statut" varchar(20) COLLATE "pg_catalog"."default" NOT NULL,
  "transaction_id" varchar(100) COLLATE "pg_catalog"."default" NOT NULL,
  "methode_paiement" varchar(30) COLLATE "pg_catalog"."default",
  "details_paiement" jsonb NOT NULL,
  "created_at" timestamptz(6) NOT NULL,
  "updated_at" timestamptz(6) NOT NULL,
  "vehicule_plaque_id" varchar(15) COLLATE "pg_catalog"."default" NOT NULL,
  "amount_stripe" int4,
  "billing_email" varchar(254) COLLATE "pg_catalog"."default",
  "billing_name" varchar(255) COLLATE "pg_catalog"."default",
  "currency_stripe" varchar(3) COLLATE "pg_catalog"."default" NOT NULL,
  "stripe_charge_id" varchar(255) COLLATE "pg_catalog"."default",
  "stripe_created" timestamptz(6),
  "stripe_customer_id" varchar(255) COLLATE "pg_catalog"."default",
  "stripe_metadata" jsonb NOT NULL,
  "stripe_payment_intent_id" varchar(255) COLLATE "pg_catalog"."default",
  "stripe_payment_method" varchar(50) COLLATE "pg_catalog"."default",
  "stripe_receipt_url" varchar(500) COLLATE "pg_catalog"."default",
  "stripe_status" varchar(30) COLLATE "pg_catalog"."default"
)
;

-- ----------------------------
-- Records of payments_paiementtaxe
-- ----------------------------

-- ----------------------------
-- Table structure for payments_qrcode
-- ----------------------------
DROP TABLE IF EXISTS "public"."payments_qrcode";
CREATE TABLE "public"."payments_qrcode" (
  "id" uuid NOT NULL,
  "annee_fiscale" int4 NOT NULL,
  "token" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "date_generation" timestamptz(6) NOT NULL,
  "date_expiration" timestamptz(6) NOT NULL,
  "est_actif" bool NOT NULL,
  "nombre_scans" int4 NOT NULL,
  "derniere_verification" timestamptz(6),
  "vehicule_plaque_id" varchar(15) COLLATE "pg_catalog"."default" NOT NULL
)
;

-- ----------------------------
-- Records of payments_qrcode
-- ----------------------------

-- ----------------------------
-- Table structure for payments_stripeconfig
-- ----------------------------
DROP TABLE IF EXISTS "public"."payments_stripeconfig";
CREATE TABLE "public"."payments_stripeconfig" (
  "id" int8 NOT NULL GENERATED BY DEFAULT AS IDENTITY (
INCREMENT 1
MINVALUE  1
MAXVALUE 9223372036854775807
START 1
CACHE 1
),
  "environment" varchar(20) COLLATE "pg_catalog"."default" NOT NULL,
  "publishable_key" varchar(255) COLLATE "pg_catalog"."default",
  "secret_key" varchar(255) COLLATE "pg_catalog"."default",
  "webhook_secret" varchar(255) COLLATE "pg_catalog"."default",
  "currency" varchar(10) COLLATE "pg_catalog"."default" NOT NULL,
  "success_url" varchar(500) COLLATE "pg_catalog"."default",
  "cancel_url" varchar(500) COLLATE "pg_catalog"."default",
  "is_active" bool NOT NULL,
  "created_at" timestamptz(6) NOT NULL,
  "updated_at" timestamptz(6) NOT NULL
)
;

-- ----------------------------
-- Records of payments_stripeconfig
-- ----------------------------

-- ----------------------------
-- Table structure for payments_stripewebhookevent
-- ----------------------------
DROP TABLE IF EXISTS "public"."payments_stripewebhookevent";
CREATE TABLE "public"."payments_stripewebhookevent" (
  "id" int8 NOT NULL GENERATED BY DEFAULT AS IDENTITY (
INCREMENT 1
MINVALUE  1
MAXVALUE 9223372036854775807
START 1
CACHE 1
),
  "stripe_event_id" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "type" varchar(100) COLLATE "pg_catalog"."default" NOT NULL,
  "data" jsonb NOT NULL,
  "processed" bool NOT NULL,
  "created_at" timestamptz(6) NOT NULL,
  "processed_at" timestamptz(6)
)
;

-- ----------------------------
-- Records of payments_stripewebhookevent
-- ----------------------------

-- ----------------------------
-- Table structure for socialaccount_socialaccount
-- ----------------------------
DROP TABLE IF EXISTS "public"."socialaccount_socialaccount";
CREATE TABLE "public"."socialaccount_socialaccount" (
  "id" int4 NOT NULL GENERATED BY DEFAULT AS IDENTITY (
INCREMENT 1
MINVALUE  1
MAXVALUE 2147483647
START 1
CACHE 1
),
  "provider" varchar(200) COLLATE "pg_catalog"."default" NOT NULL,
  "uid" varchar(191) COLLATE "pg_catalog"."default" NOT NULL,
  "last_login" timestamptz(6) NOT NULL,
  "date_joined" timestamptz(6) NOT NULL,
  "extra_data" jsonb NOT NULL,
  "user_id" int4 NOT NULL
)
;

-- ----------------------------
-- Records of socialaccount_socialaccount
-- ----------------------------

-- ----------------------------
-- Table structure for socialaccount_socialapp
-- ----------------------------
DROP TABLE IF EXISTS "public"."socialaccount_socialapp";
CREATE TABLE "public"."socialaccount_socialapp" (
  "id" int4 NOT NULL GENERATED BY DEFAULT AS IDENTITY (
INCREMENT 1
MINVALUE  1
MAXVALUE 2147483647
START 1
CACHE 1
),
  "provider" varchar(30) COLLATE "pg_catalog"."default" NOT NULL,
  "name" varchar(40) COLLATE "pg_catalog"."default" NOT NULL,
  "client_id" varchar(191) COLLATE "pg_catalog"."default" NOT NULL,
  "secret" varchar(191) COLLATE "pg_catalog"."default" NOT NULL,
  "key" varchar(191) COLLATE "pg_catalog"."default" NOT NULL,
  "provider_id" varchar(200) COLLATE "pg_catalog"."default" NOT NULL,
  "settings" jsonb NOT NULL
)
;

-- ----------------------------
-- Records of socialaccount_socialapp
-- ----------------------------

-- ----------------------------
-- Table structure for socialaccount_socialapp_sites
-- ----------------------------
DROP TABLE IF EXISTS "public"."socialaccount_socialapp_sites";
CREATE TABLE "public"."socialaccount_socialapp_sites" (
  "id" int8 NOT NULL GENERATED BY DEFAULT AS IDENTITY (
INCREMENT 1
MINVALUE  1
MAXVALUE 9223372036854775807
START 1
CACHE 1
),
  "socialapp_id" int4 NOT NULL,
  "site_id" int4 NOT NULL
)
;

-- ----------------------------
-- Records of socialaccount_socialapp_sites
-- ----------------------------

-- ----------------------------
-- Table structure for socialaccount_socialtoken
-- ----------------------------
DROP TABLE IF EXISTS "public"."socialaccount_socialtoken";
CREATE TABLE "public"."socialaccount_socialtoken" (
  "id" int4 NOT NULL GENERATED BY DEFAULT AS IDENTITY (
INCREMENT 1
MINVALUE  1
MAXVALUE 2147483647
START 1
CACHE 1
),
  "token" text COLLATE "pg_catalog"."default" NOT NULL,
  "token_secret" text COLLATE "pg_catalog"."default" NOT NULL,
  "expires_at" timestamptz(6),
  "account_id" int4 NOT NULL,
  "app_id" int4
)
;

-- ----------------------------
-- Records of socialaccount_socialtoken
-- ----------------------------

-- ----------------------------
-- Table structure for vehicles_documentvehicule
-- ----------------------------
DROP TABLE IF EXISTS "public"."vehicles_documentvehicule";
CREATE TABLE "public"."vehicles_documentvehicule" (
  "id" uuid NOT NULL,
  "document_type" varchar(50) COLLATE "pg_catalog"."default" NOT NULL,
  "fichier" varchar(100) COLLATE "pg_catalog"."default" NOT NULL,
  "note" text COLLATE "pg_catalog"."default" NOT NULL,
  "expiration_date" date,
  "verification_status" varchar(20) COLLATE "pg_catalog"."default" NOT NULL,
  "verification_comment" text COLLATE "pg_catalog"."default" NOT NULL,
  "created_at" timestamptz(6) NOT NULL,
  "updated_at" timestamptz(6) NOT NULL,
  "uploaded_by_id" int4 NOT NULL,
  "vehicule_id" varchar(15) COLLATE "pg_catalog"."default" NOT NULL
)
;

-- ----------------------------
-- Records of vehicles_documentvehicule
-- ----------------------------
INSERT INTO "public"."vehicles_documentvehicule" VALUES ('f8b5849d-4f10-4f03-a115-b5eab1a8cf72', 'photo_plaque', 'vehicle_documents/2025/11/04/sample.jpg', 'Test upload via client', NULL, 'soumis', '', '2025-11-04 11:27:53.457274+03', '2025-11-04 11:27:53.457299+03', 19, '1234 TAA');

-- ----------------------------
-- Table structure for vehicles_grilletarifaire
-- ----------------------------
DROP TABLE IF EXISTS "public"."vehicles_grilletarifaire";
CREATE TABLE "public"."vehicles_grilletarifaire" (
  "id" int8 NOT NULL GENERATED BY DEFAULT AS IDENTITY (
INCREMENT 1
MINVALUE  1
MAXVALUE 9223372036854775807
START 1
CACHE 1
),
  "puissance_min_cv" int4 NOT NULL,
  "puissance_max_cv" int4,
  "source_energie" varchar(20) COLLATE "pg_catalog"."default" NOT NULL,
  "age_min_annees" int4 NOT NULL,
  "age_max_annees" int4,
  "montant_ariary" numeric(12,2) NOT NULL,
  "annee_fiscale" int4 NOT NULL,
  "est_active" bool NOT NULL,
  "created_at" timestamptz(6) NOT NULL
)
;

-- ----------------------------
-- Records of vehicles_grilletarifaire
-- ----------------------------
INSERT INTO "public"."vehicles_grilletarifaire" VALUES (17, 1, 4, 'Essence', 0, 5, 15000.00, 2025, 't', '2025-11-01 06:35:22.430604+03');
INSERT INTO "public"."vehicles_grilletarifaire" VALUES (18, 1, 4, 'Diesel', 0, 5, 20000.00, 2025, 't', '2025-11-01 06:35:22.437874+03');
INSERT INTO "public"."vehicles_grilletarifaire" VALUES (19, 1, 4, 'Electrique', 0, 5, 5000.00, 2025, 't', '2025-11-01 06:35:22.441806+03');
INSERT INTO "public"."vehicles_grilletarifaire" VALUES (20, 1, 4, 'Hybride', 0, 5, 10000.00, 2025, 't', '2025-11-01 06:35:22.448903+03');
INSERT INTO "public"."vehicles_grilletarifaire" VALUES (21, 1, 4, 'Essence', 6, 10, 40000.00, 2025, 't', '2025-11-01 06:35:22.452621+03');
INSERT INTO "public"."vehicles_grilletarifaire" VALUES (22, 1, 4, 'Diesel', 6, 10, 45000.00, 2025, 't', '2025-11-01 06:35:22.457296+03');
INSERT INTO "public"."vehicles_grilletarifaire" VALUES (23, 1, 4, 'Electrique', 6, 10, 30000.00, 2025, 't', '2025-11-01 06:35:22.460097+03');
INSERT INTO "public"."vehicles_grilletarifaire" VALUES (24, 1, 4, 'Hybride', 6, 10, 35000.00, 2025, 't', '2025-11-01 06:35:22.462779+03');
INSERT INTO "public"."vehicles_grilletarifaire" VALUES (25, 1, 4, 'Essence', 11, 20, 90000.00, 2025, 't', '2025-11-01 06:35:22.465308+03');
INSERT INTO "public"."vehicles_grilletarifaire" VALUES (26, 1, 4, 'Diesel', 11, 20, 95000.00, 2025, 't', '2025-11-01 06:35:22.468508+03');
INSERT INTO "public"."vehicles_grilletarifaire" VALUES (27, 1, 4, 'Electrique', 11, 20, 80000.00, 2025, 't', '2025-11-01 06:35:22.471029+03');
INSERT INTO "public"."vehicles_grilletarifaire" VALUES (28, 1, 4, 'Hybride', 11, 20, 85000.00, 2025, 't', '2025-11-01 06:35:22.473349+03');
INSERT INTO "public"."vehicles_grilletarifaire" VALUES (29, 1, 4, 'Essence', 21, NULL, 115000.00, 2025, 't', '2025-11-01 06:35:22.475871+03');
INSERT INTO "public"."vehicles_grilletarifaire" VALUES (30, 1, 4, 'Diesel', 21, NULL, 120000.00, 2025, 't', '2025-11-01 06:35:22.478519+03');
INSERT INTO "public"."vehicles_grilletarifaire" VALUES (31, 1, 4, 'Electrique', 21, NULL, 105000.00, 2025, 't', '2025-11-01 06:35:22.481134+03');
INSERT INTO "public"."vehicles_grilletarifaire" VALUES (32, 1, 4, 'Hybride', 21, NULL, 110000.00, 2025, 't', '2025-11-01 06:35:22.48431+03');
INSERT INTO "public"."vehicles_grilletarifaire" VALUES (33, 5, 9, 'Essence', 0, 5, 30000.00, 2025, 't', '2025-11-01 06:35:22.487053+03');
INSERT INTO "public"."vehicles_grilletarifaire" VALUES (34, 5, 9, 'Diesel', 0, 5, 40000.00, 2025, 't', '2025-11-01 06:35:22.489576+03');
INSERT INTO "public"."vehicles_grilletarifaire" VALUES (35, 5, 9, 'Electrique', 0, 5, 10000.00, 2025, 't', '2025-11-01 06:35:22.492028+03');
INSERT INTO "public"."vehicles_grilletarifaire" VALUES (36, 5, 9, 'Hybride', 0, 5, 20000.00, 2025, 't', '2025-11-01 06:35:22.494988+03');
INSERT INTO "public"."vehicles_grilletarifaire" VALUES (37, 5, 9, 'Essence', 6, 10, 55000.00, 2025, 't', '2025-11-01 06:35:22.49766+03');
INSERT INTO "public"."vehicles_grilletarifaire" VALUES (38, 5, 9, 'Diesel', 6, 10, 65000.00, 2025, 't', '2025-11-01 06:35:22.500429+03');
INSERT INTO "public"."vehicles_grilletarifaire" VALUES (39, 5, 9, 'Electrique', 6, 10, 35000.00, 2025, 't', '2025-11-01 06:35:22.503467+03');
INSERT INTO "public"."vehicles_grilletarifaire" VALUES (40, 5, 9, 'Hybride', 6, 10, 45000.00, 2025, 't', '2025-11-01 06:35:22.505901+03');
INSERT INTO "public"."vehicles_grilletarifaire" VALUES (41, 5, 9, 'Essence', 11, 20, 105000.00, 2025, 't', '2025-11-01 06:35:22.50835+03');
INSERT INTO "public"."vehicles_grilletarifaire" VALUES (42, 5, 9, 'Diesel', 11, 20, 115000.00, 2025, 't', '2025-11-01 06:35:22.510754+03');
INSERT INTO "public"."vehicles_grilletarifaire" VALUES (43, 5, 9, 'Electrique', 11, 20, 85000.00, 2025, 't', '2025-11-01 06:35:22.513225+03');
INSERT INTO "public"."vehicles_grilletarifaire" VALUES (44, 5, 9, 'Hybride', 11, 20, 95000.00, 2025, 't', '2025-11-01 06:35:22.515626+03');
INSERT INTO "public"."vehicles_grilletarifaire" VALUES (45, 5, 9, 'Essence', 21, NULL, 130000.00, 2025, 't', '2025-11-01 06:35:22.51865+03');
INSERT INTO "public"."vehicles_grilletarifaire" VALUES (46, 5, 9, 'Diesel', 21, NULL, 140000.00, 2025, 't', '2025-11-01 06:35:22.521392+03');
INSERT INTO "public"."vehicles_grilletarifaire" VALUES (47, 5, 9, 'Electrique', 21, NULL, 110000.00, 2025, 't', '2025-11-01 06:35:22.524373+03');
INSERT INTO "public"."vehicles_grilletarifaire" VALUES (48, 5, 9, 'Hybride', 21, NULL, 120000.00, 2025, 't', '2025-11-01 06:35:22.527443+03');
INSERT INTO "public"."vehicles_grilletarifaire" VALUES (49, 10, 12, 'Essence', 0, 5, 60000.00, 2025, 't', '2025-11-01 06:35:22.529786+03');
INSERT INTO "public"."vehicles_grilletarifaire" VALUES (50, 10, 12, 'Diesel', 0, 5, 80000.00, 2025, 't', '2025-11-01 06:35:22.532102+03');
INSERT INTO "public"."vehicles_grilletarifaire" VALUES (51, 10, 12, 'Electrique', 0, 5, 20000.00, 2025, 't', '2025-11-01 06:35:22.535545+03');
INSERT INTO "public"."vehicles_grilletarifaire" VALUES (52, 10, 12, 'Hybride', 0, 5, 40000.00, 2025, 't', '2025-11-01 06:35:22.538042+03');
INSERT INTO "public"."vehicles_grilletarifaire" VALUES (53, 10, 12, 'Essence', 6, 10, 85000.00, 2025, 't', '2025-11-01 06:35:22.540497+03');
INSERT INTO "public"."vehicles_grilletarifaire" VALUES (54, 10, 12, 'Diesel', 6, 10, 105000.00, 2025, 't', '2025-11-01 06:35:22.542823+03');
INSERT INTO "public"."vehicles_grilletarifaire" VALUES (55, 10, 12, 'Electrique', 6, 10, 45000.00, 2025, 't', '2025-11-01 06:35:22.545219+03');
INSERT INTO "public"."vehicles_grilletarifaire" VALUES (56, 10, 12, 'Hybride', 6, 10, 65000.00, 2025, 't', '2025-11-01 06:35:22.547682+03');
INSERT INTO "public"."vehicles_grilletarifaire" VALUES (57, 10, 12, 'Essence', 11, 20, 135000.00, 2025, 't', '2025-11-01 06:35:22.550577+03');
INSERT INTO "public"."vehicles_grilletarifaire" VALUES (58, 10, 12, 'Diesel', 11, 20, 155000.00, 2025, 't', '2025-11-01 06:35:22.553083+03');
INSERT INTO "public"."vehicles_grilletarifaire" VALUES (59, 10, 12, 'Electrique', 11, 20, 95000.00, 2025, 't', '2025-11-01 06:35:22.555492+03');
INSERT INTO "public"."vehicles_grilletarifaire" VALUES (60, 10, 12, 'Hybride', 11, 20, 115000.00, 2025, 't', '2025-11-01 06:35:22.55771+03');
INSERT INTO "public"."vehicles_grilletarifaire" VALUES (61, 10, 12, 'Essence', 21, NULL, 160000.00, 2025, 't', '2025-11-01 06:35:22.559822+03');
INSERT INTO "public"."vehicles_grilletarifaire" VALUES (62, 10, 12, 'Diesel', 21, NULL, 180000.00, 2025, 't', '2025-11-01 06:35:22.562019+03');
INSERT INTO "public"."vehicles_grilletarifaire" VALUES (63, 10, 12, 'Electrique', 21, NULL, 120000.00, 2025, 't', '2025-11-01 06:35:22.564161+03');
INSERT INTO "public"."vehicles_grilletarifaire" VALUES (64, 10, 12, 'Hybride', 21, NULL, 140000.00, 2025, 't', '2025-11-01 06:35:22.566634+03');
INSERT INTO "public"."vehicles_grilletarifaire" VALUES (65, 13, 15, 'Essence', 0, 5, 90000.00, 2025, 't', '2025-11-01 06:35:22.569215+03');
INSERT INTO "public"."vehicles_grilletarifaire" VALUES (66, 13, 15, 'Diesel', 0, 5, 120000.00, 2025, 't', '2025-11-01 06:35:22.571601+03');
INSERT INTO "public"."vehicles_grilletarifaire" VALUES (67, 13, 15, 'Electrique', 0, 5, 30000.00, 2025, 't', '2025-11-01 06:35:22.573749+03');
INSERT INTO "public"."vehicles_grilletarifaire" VALUES (68, 13, 15, 'Hybride', 0, 5, 60000.00, 2025, 't', '2025-11-01 06:35:22.575804+03');
INSERT INTO "public"."vehicles_grilletarifaire" VALUES (69, 13, 15, 'Essence', 6, 10, 115000.00, 2025, 't', '2025-11-01 06:35:22.577847+03');
INSERT INTO "public"."vehicles_grilletarifaire" VALUES (70, 13, 15, 'Diesel', 6, 10, 145000.00, 2025, 't', '2025-11-01 06:35:22.580005+03');
INSERT INTO "public"."vehicles_grilletarifaire" VALUES (71, 13, 15, 'Electrique', 6, 10, 55000.00, 2025, 't', '2025-11-01 06:35:22.582044+03');
INSERT INTO "public"."vehicles_grilletarifaire" VALUES (72, 13, 15, 'Hybride', 6, 10, 85000.00, 2025, 't', '2025-11-01 06:35:22.584767+03');
INSERT INTO "public"."vehicles_grilletarifaire" VALUES (73, 13, 15, 'Essence', 11, 20, 165000.00, 2025, 't', '2025-11-01 06:35:22.587843+03');
INSERT INTO "public"."vehicles_grilletarifaire" VALUES (74, 13, 15, 'Diesel', 11, 20, 195000.00, 2025, 't', '2025-11-01 06:35:22.590872+03');
INSERT INTO "public"."vehicles_grilletarifaire" VALUES (75, 13, 15, 'Electrique', 11, 20, 105000.00, 2025, 't', '2025-11-01 06:35:22.593792+03');
INSERT INTO "public"."vehicles_grilletarifaire" VALUES (76, 13, 15, 'Hybride', 11, 20, 135000.00, 2025, 't', '2025-11-01 06:35:22.596003+03');
INSERT INTO "public"."vehicles_grilletarifaire" VALUES (77, 13, 15, 'Essence', 21, NULL, 190000.00, 2025, 't', '2025-11-01 06:35:22.597949+03');
INSERT INTO "public"."vehicles_grilletarifaire" VALUES (78, 13, 15, 'Diesel', 21, NULL, 220000.00, 2025, 't', '2025-11-01 06:35:22.6003+03');
INSERT INTO "public"."vehicles_grilletarifaire" VALUES (79, 13, 15, 'Electrique', 21, NULL, 130000.00, 2025, 't', '2025-11-01 06:35:22.602535+03');
INSERT INTO "public"."vehicles_grilletarifaire" VALUES (80, 13, 15, 'Hybride', 21, NULL, 160000.00, 2025, 't', '2025-11-01 06:35:22.604378+03');
INSERT INTO "public"."vehicles_grilletarifaire" VALUES (81, 16, NULL, 'Essence', 0, 5, 180000.00, 2025, 't', '2025-11-01 06:35:22.606114+03');
INSERT INTO "public"."vehicles_grilletarifaire" VALUES (82, 16, NULL, 'Diesel', 0, 5, 240000.00, 2025, 't', '2025-11-01 06:35:22.607864+03');
INSERT INTO "public"."vehicles_grilletarifaire" VALUES (83, 16, NULL, 'Electrique', 0, 5, 60000.00, 2025, 't', '2025-11-01 06:35:22.60959+03');
INSERT INTO "public"."vehicles_grilletarifaire" VALUES (84, 16, NULL, 'Hybride', 0, 5, 120000.00, 2025, 't', '2025-11-01 06:35:22.611359+03');
INSERT INTO "public"."vehicles_grilletarifaire" VALUES (85, 16, NULL, 'Essence', 6, 10, 205000.00, 2025, 't', '2025-11-01 06:35:22.613217+03');
INSERT INTO "public"."vehicles_grilletarifaire" VALUES (86, 16, NULL, 'Diesel', 6, 10, 265000.00, 2025, 't', '2025-11-01 06:35:22.614891+03');
INSERT INTO "public"."vehicles_grilletarifaire" VALUES (87, 16, NULL, 'Electrique', 6, 10, 85000.00, 2025, 't', '2025-11-01 06:35:22.6172+03');
INSERT INTO "public"."vehicles_grilletarifaire" VALUES (88, 16, NULL, 'Hybride', 6, 10, 145000.00, 2025, 't', '2025-11-01 06:35:22.619498+03');
INSERT INTO "public"."vehicles_grilletarifaire" VALUES (89, 16, NULL, 'Essence', 11, 20, 255000.00, 2025, 't', '2025-11-01 06:35:22.621187+03');
INSERT INTO "public"."vehicles_grilletarifaire" VALUES (90, 16, NULL, 'Diesel', 11, 20, 315000.00, 2025, 't', '2025-11-01 06:35:22.622821+03');
INSERT INTO "public"."vehicles_grilletarifaire" VALUES (91, 16, NULL, 'Electrique', 11, 20, 135000.00, 2025, 't', '2025-11-01 06:35:22.624528+03');
INSERT INTO "public"."vehicles_grilletarifaire" VALUES (92, 16, NULL, 'Hybride', 11, 20, 195000.00, 2025, 't', '2025-11-01 06:35:22.62621+03');
INSERT INTO "public"."vehicles_grilletarifaire" VALUES (93, 16, NULL, 'Essence', 21, NULL, 280000.00, 2025, 't', '2025-11-01 06:35:22.627858+03');
INSERT INTO "public"."vehicles_grilletarifaire" VALUES (94, 16, NULL, 'Diesel', 21, NULL, 340000.00, 2025, 't', '2025-11-01 06:35:22.629465+03');
INSERT INTO "public"."vehicles_grilletarifaire" VALUES (95, 16, NULL, 'Electrique', 21, NULL, 160000.00, 2025, 't', '2025-11-01 06:35:22.631235+03');
INSERT INTO "public"."vehicles_grilletarifaire" VALUES (96, 16, NULL, 'Hybride', 21, NULL, 220000.00, 2025, 't', '2025-11-01 06:35:22.633736+03');

-- ----------------------------
-- Table structure for vehicles_vehicletype
-- ----------------------------
DROP TABLE IF EXISTS "public"."vehicles_vehicletype";
CREATE TABLE "public"."vehicles_vehicletype" (
  "id" int8 NOT NULL GENERATED BY DEFAULT AS IDENTITY (
INCREMENT 1
MINVALUE  1
MAXVALUE 9223372036854775807
START 1
CACHE 1
),
  "nom" varchar(50) COLLATE "pg_catalog"."default" NOT NULL,
  "description" text COLLATE "pg_catalog"."default" NOT NULL,
  "est_actif" bool NOT NULL,
  "ordre_affichage" int4 NOT NULL,
  "created_at" timestamptz(6) NOT NULL,
  "updated_at" timestamptz(6) NOT NULL
)
;

-- ----------------------------
-- Records of vehicles_vehicletype
-- ----------------------------
INSERT INTO "public"."vehicles_vehicletype" VALUES (1, 'Voiture', 'Véhicule de tourisme personnel', 't', 1, '2025-11-02 16:59:21.961091+03', '2025-11-02 16:59:21.961106+03');
INSERT INTO "public"."vehicles_vehicletype" VALUES (2, 'Moto', 'Motocyclette', 't', 2, '2025-11-02 16:59:21.96518+03', '2025-11-02 16:59:21.965191+03');
INSERT INTO "public"."vehicles_vehicletype" VALUES (3, 'Scooter', 'Scooter ou cyclomoteur', 't', 3, '2025-11-02 16:59:21.967526+03', '2025-11-02 16:59:21.967538+03');
INSERT INTO "public"."vehicles_vehicletype" VALUES (4, 'Camionnette', 'Véhicule utilitaire léger', 't', 4, '2025-11-02 16:59:21.969678+03', '2025-11-02 16:59:21.969695+03');
INSERT INTO "public"."vehicles_vehicletype" VALUES (5, 'Camion', 'Véhicule de transport de marchandises', 't', 5, '2025-11-02 16:59:21.971883+03', '2025-11-02 16:59:21.971894+03');
INSERT INTO "public"."vehicles_vehicletype" VALUES (6, 'Bus', 'Véhicule de transport de passagers', 't', 6, '2025-11-02 16:59:21.973812+03', '2025-11-02 16:59:21.973822+03');
INSERT INTO "public"."vehicles_vehicletype" VALUES (7, 'Autre', 'Autre type de véhicule', 't', 7, '2025-11-02 16:59:21.975669+03', '2025-11-02 16:59:21.975677+03');

-- ----------------------------
-- Table structure for vehicles_vehicule
-- ----------------------------
DROP TABLE IF EXISTS "public"."vehicles_vehicule";
CREATE TABLE "public"."vehicles_vehicule" (
  "plaque_immatriculation" varchar(15) COLLATE "pg_catalog"."default" NOT NULL,
  "puissance_fiscale_cv" int4 NOT NULL,
  "cylindree_cm3" int4 NOT NULL,
  "source_energie" varchar(20) COLLATE "pg_catalog"."default" NOT NULL,
  "date_premiere_circulation" date NOT NULL,
  "categorie_vehicule" varchar(50) COLLATE "pg_catalog"."default" NOT NULL,
  "type_vehicule_id" int8 NOT NULL,
  "specifications_techniques" jsonb NOT NULL,
  "est_actif" bool NOT NULL,
  "created_at" timestamptz(6) NOT NULL,
  "updated_at" timestamptz(6) NOT NULL,
  "proprietaire_id" int4 NOT NULL
)
;

-- ----------------------------
-- Records of vehicles_vehicule
-- ----------------------------
INSERT INTO "public"."vehicles_vehicule" VALUES ('1234 TAA', 13, 1600, 'Essence', '2018-11-04', 'Personnel', 1, '{}', 't', '2025-11-04 11:24:37.843097+03', '2025-11-04 11:24:37.843157+03', 19);

-- ----------------------------
-- Alter sequences owned by
-- ----------------------------
ALTER SEQUENCE "public"."account_emailaddress_id_seq"
OWNED BY "public"."account_emailaddress"."id";
SELECT setval('"public"."account_emailaddress_id_seq"', 1, false);

-- ----------------------------
-- Alter sequences owned by
-- ----------------------------
ALTER SEQUENCE "public"."account_emailconfirmation_id_seq"
OWNED BY "public"."account_emailconfirmation"."id";
SELECT setval('"public"."account_emailconfirmation_id_seq"', 1, false);

-- ----------------------------
-- Alter sequences owned by
-- ----------------------------
ALTER SEQUENCE "public"."administration_adminsession_id_seq"
OWNED BY "public"."administration_adminsession"."id";
SELECT setval('"public"."administration_adminsession_id_seq"', 1, false);

-- ----------------------------
-- Alter sequences owned by
-- ----------------------------
ALTER SEQUENCE "public"."administration_adminuserprofile_id_seq"
OWNED BY "public"."administration_adminuserprofile"."id";
SELECT setval('"public"."administration_adminuserprofile_id_seq"', 1, false);

-- ----------------------------
-- Alter sequences owned by
-- ----------------------------
ALTER SEQUENCE "public"."administration_agentverification_id_seq"
OWNED BY "public"."administration_agentverification"."id";
SELECT setval('"public"."administration_agentverification_id_seq"', 1, false);

-- ----------------------------
-- Alter sequences owned by
-- ----------------------------
ALTER SEQUENCE "public"."administration_configurationsysteme_id_seq"
OWNED BY "public"."administration_configurationsysteme"."id";
SELECT setval('"public"."administration_configurationsysteme_id_seq"', 1, false);

-- ----------------------------
-- Alter sequences owned by
-- ----------------------------
ALTER SEQUENCE "public"."administration_dataversion_id_seq"
OWNED BY "public"."administration_dataversion"."id";
SELECT setval('"public"."administration_dataversion_id_seq"', 1, false);

-- ----------------------------
-- Alter sequences owned by
-- ----------------------------
ALTER SEQUENCE "public"."administration_permissiongroup_id_seq"
OWNED BY "public"."administration_permissiongroup"."id";
SELECT setval('"public"."administration_permissiongroup_id_seq"', 1, false);

-- ----------------------------
-- Alter sequences owned by
-- ----------------------------
ALTER SEQUENCE "public"."administration_permissiongroup_users_id_seq"
OWNED BY "public"."administration_permissiongroup_users"."id";
SELECT setval('"public"."administration_permissiongroup_users_id_seq"', 1, false);

-- ----------------------------
-- Alter sequences owned by
-- ----------------------------
ALTER SEQUENCE "public"."administration_statistiquesplateforme_id_seq"
OWNED BY "public"."administration_statistiquesplateforme"."id";
SELECT setval('"public"."administration_statistiquesplateforme_id_seq"', 1, false);

-- ----------------------------
-- Alter sequences owned by
-- ----------------------------
ALTER SEQUENCE "public"."auth_group_id_seq"
OWNED BY "public"."auth_group"."id";
SELECT setval('"public"."auth_group_id_seq"', 1, false);

-- ----------------------------
-- Alter sequences owned by
-- ----------------------------
ALTER SEQUENCE "public"."auth_group_permissions_id_seq"
OWNED BY "public"."auth_group_permissions"."id";
SELECT setval('"public"."auth_group_permissions_id_seq"', 1, false);

-- ----------------------------
-- Alter sequences owned by
-- ----------------------------
ALTER SEQUENCE "public"."auth_permission_id_seq"
OWNED BY "public"."auth_permission"."id";
SELECT setval('"public"."auth_permission_id_seq"', 156, true);

-- ----------------------------
-- Alter sequences owned by
-- ----------------------------
ALTER SEQUENCE "public"."auth_user_groups_id_seq"
OWNED BY "public"."auth_user_groups"."id";
SELECT setval('"public"."auth_user_groups_id_seq"', 1, false);

-- ----------------------------
-- Alter sequences owned by
-- ----------------------------
ALTER SEQUENCE "public"."auth_user_id_seq"
OWNED BY "public"."auth_user"."id";
SELECT setval('"public"."auth_user_id_seq"', 19, true);

-- ----------------------------
-- Alter sequences owned by
-- ----------------------------
ALTER SEQUENCE "public"."auth_user_user_permissions_id_seq"
OWNED BY "public"."auth_user_user_permissions"."id";
SELECT setval('"public"."auth_user_user_permissions_id_seq"', 1, false);

-- ----------------------------
-- Alter sequences owned by
-- ----------------------------
ALTER SEQUENCE "public"."django_admin_log_id_seq"
OWNED BY "public"."django_admin_log"."id";
SELECT setval('"public"."django_admin_log_id_seq"', 1, false);

-- ----------------------------
-- Alter sequences owned by
-- ----------------------------
ALTER SEQUENCE "public"."django_content_type_id_seq"
OWNED BY "public"."django_content_type"."id";
SELECT setval('"public"."django_content_type_id_seq"', 39, true);

-- ----------------------------
-- Alter sequences owned by
-- ----------------------------
ALTER SEQUENCE "public"."django_migrations_id_seq"
OWNED BY "public"."django_migrations"."id";
SELECT setval('"public"."django_migrations_id_seq"', 51, true);

-- ----------------------------
-- Alter sequences owned by
-- ----------------------------
ALTER SEQUENCE "public"."django_site_id_seq"
OWNED BY "public"."django_site"."id";
SELECT setval('"public"."django_site_id_seq"', 1, true);

-- ----------------------------
-- Alter sequences owned by
-- ----------------------------
ALTER SEQUENCE "public"."notifications_notificationtemplate_id_seq"
OWNED BY "public"."notifications_notificationtemplate"."id";
SELECT setval('"public"."notifications_notificationtemplate_id_seq"', 1, false);

-- ----------------------------
-- Alter sequences owned by
-- ----------------------------
ALTER SEQUENCE "public"."payments_stripeconfig_id_seq"
OWNED BY "public"."payments_stripeconfig"."id";
SELECT setval('"public"."payments_stripeconfig_id_seq"', 1, false);

-- ----------------------------
-- Alter sequences owned by
-- ----------------------------
ALTER SEQUENCE "public"."payments_stripewebhookevent_id_seq"
OWNED BY "public"."payments_stripewebhookevent"."id";
SELECT setval('"public"."payments_stripewebhookevent_id_seq"', 1, false);

-- ----------------------------
-- Alter sequences owned by
-- ----------------------------
ALTER SEQUENCE "public"."socialaccount_socialaccount_id_seq"
OWNED BY "public"."socialaccount_socialaccount"."id";
SELECT setval('"public"."socialaccount_socialaccount_id_seq"', 1, false);

-- ----------------------------
-- Alter sequences owned by
-- ----------------------------
ALTER SEQUENCE "public"."socialaccount_socialapp_id_seq"
OWNED BY "public"."socialaccount_socialapp"."id";
SELECT setval('"public"."socialaccount_socialapp_id_seq"', 1, false);

-- ----------------------------
-- Alter sequences owned by
-- ----------------------------
ALTER SEQUENCE "public"."socialaccount_socialapp_sites_id_seq"
OWNED BY "public"."socialaccount_socialapp_sites"."id";
SELECT setval('"public"."socialaccount_socialapp_sites_id_seq"', 1, false);

-- ----------------------------
-- Alter sequences owned by
-- ----------------------------
ALTER SEQUENCE "public"."socialaccount_socialtoken_id_seq"
OWNED BY "public"."socialaccount_socialtoken"."id";
SELECT setval('"public"."socialaccount_socialtoken_id_seq"', 1, false);

-- ----------------------------
-- Alter sequences owned by
-- ----------------------------
ALTER SEQUENCE "public"."vehicles_grilletarifaire_id_seq"
OWNED BY "public"."vehicles_grilletarifaire"."id";
SELECT setval('"public"."vehicles_grilletarifaire_id_seq"', 96, true);

-- ----------------------------
-- Alter sequences owned by
-- ----------------------------
ALTER SEQUENCE "public"."vehicles_vehicletype_id_seq"
OWNED BY "public"."vehicles_vehicletype"."id";
SELECT setval('"public"."vehicles_vehicletype_id_seq"', 7, true);

-- ----------------------------
-- Auto increment value for account_emailaddress
-- ----------------------------
SELECT setval('"public"."account_emailaddress_id_seq"', 1, false);

-- ----------------------------
-- Indexes structure for table account_emailaddress
-- ----------------------------
CREATE INDEX "account_emailaddress_email_03be32b2" ON "public"."account_emailaddress" USING btree (
  "email" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);
CREATE INDEX "account_emailaddress_email_03be32b2_like" ON "public"."account_emailaddress" USING btree (
  "email" COLLATE "pg_catalog"."default" "pg_catalog"."varchar_pattern_ops" ASC NULLS LAST
);
CREATE INDEX "account_emailaddress_user_id_2c513194" ON "public"."account_emailaddress" USING btree (
  "user_id" "pg_catalog"."int4_ops" ASC NULLS LAST
);
CREATE UNIQUE INDEX "unique_primary_email" ON "public"."account_emailaddress" USING btree (
  "user_id" "pg_catalog"."int4_ops" ASC NULLS LAST,
  "primary" "pg_catalog"."bool_ops" ASC NULLS LAST
) WHERE "primary";
CREATE UNIQUE INDEX "unique_verified_email" ON "public"."account_emailaddress" USING btree (
  "email" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
) WHERE verified;

-- ----------------------------
-- Uniques structure for table account_emailaddress
-- ----------------------------
ALTER TABLE "public"."account_emailaddress" ADD CONSTRAINT "account_emailaddress_user_id_email_987c8728_uniq" UNIQUE ("user_id", "email");

-- ----------------------------
-- Primary Key structure for table account_emailaddress
-- ----------------------------
ALTER TABLE "public"."account_emailaddress" ADD CONSTRAINT "account_emailaddress_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Auto increment value for account_emailconfirmation
-- ----------------------------
SELECT setval('"public"."account_emailconfirmation_id_seq"', 1, false);

-- ----------------------------
-- Indexes structure for table account_emailconfirmation
-- ----------------------------
CREATE INDEX "account_emailconfirmation_email_address_id_5b7f8c58" ON "public"."account_emailconfirmation" USING btree (
  "email_address_id" "pg_catalog"."int4_ops" ASC NULLS LAST
);
CREATE INDEX "account_emailconfirmation_key_f43612bd_like" ON "public"."account_emailconfirmation" USING btree (
  "key" COLLATE "pg_catalog"."default" "pg_catalog"."varchar_pattern_ops" ASC NULLS LAST
);

-- ----------------------------
-- Uniques structure for table account_emailconfirmation
-- ----------------------------
ALTER TABLE "public"."account_emailconfirmation" ADD CONSTRAINT "account_emailconfirmation_key_key" UNIQUE ("key");

-- ----------------------------
-- Primary Key structure for table account_emailconfirmation
-- ----------------------------
ALTER TABLE "public"."account_emailconfirmation" ADD CONSTRAINT "account_emailconfirmation_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Auto increment value for administration_adminsession
-- ----------------------------
SELECT setval('"public"."administration_adminsession_id_seq"', 1, false);

-- ----------------------------
-- Indexes structure for table administration_adminsession
-- ----------------------------
CREATE INDEX "administrat_last_ac_0e5e8c_idx" ON "public"."administration_adminsession" USING btree (
  "last_activity" "pg_catalog"."timestamptz_ops" ASC NULLS LAST
);
CREATE INDEX "administrat_session_c2b3b6_idx" ON "public"."administration_adminsession" USING btree (
  "session_key" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);
CREATE INDEX "administrat_user_id_788bba_idx" ON "public"."administration_adminsession" USING btree (
  "user_id" "pg_catalog"."int4_ops" ASC NULLS LAST,
  "is_active" "pg_catalog"."bool_ops" ASC NULLS LAST
);
CREATE INDEX "administration_adminsession_session_key_32b95ef0_like" ON "public"."administration_adminsession" USING btree (
  "session_key" COLLATE "pg_catalog"."default" "pg_catalog"."varchar_pattern_ops" ASC NULLS LAST
);
CREATE INDEX "administration_adminsession_user_id_241fef87" ON "public"."administration_adminsession" USING btree (
  "user_id" "pg_catalog"."int4_ops" ASC NULLS LAST
);

-- ----------------------------
-- Uniques structure for table administration_adminsession
-- ----------------------------
ALTER TABLE "public"."administration_adminsession" ADD CONSTRAINT "administration_adminsession_session_key_key" UNIQUE ("session_key");

-- ----------------------------
-- Primary Key structure for table administration_adminsession
-- ----------------------------
ALTER TABLE "public"."administration_adminsession" ADD CONSTRAINT "administration_adminsession_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Auto increment value for administration_adminuserprofile
-- ----------------------------
SELECT setval('"public"."administration_adminuserprofile_id_seq"', 1, false);

-- ----------------------------
-- Indexes structure for table administration_adminuserprofile
-- ----------------------------
CREATE INDEX "administrat_is_2fa__6d4aff_idx" ON "public"."administration_adminuserprofile" USING btree (
  "is_2fa_enabled" "pg_catalog"."bool_ops" ASC NULLS LAST
);
CREATE INDEX "administrat_last_lo_f09251_idx" ON "public"."administration_adminuserprofile" USING btree (
  "last_login_ip" "pg_catalog"."inet_ops" ASC NULLS LAST
);
CREATE INDEX "administrat_user_id_ed3da2_idx" ON "public"."administration_adminuserprofile" USING btree (
  "user_id" "pg_catalog"."int4_ops" ASC NULLS LAST
);

-- ----------------------------
-- Uniques structure for table administration_adminuserprofile
-- ----------------------------
ALTER TABLE "public"."administration_adminuserprofile" ADD CONSTRAINT "administration_adminuserprofile_user_id_key" UNIQUE ("user_id");

-- ----------------------------
-- Primary Key structure for table administration_adminuserprofile
-- ----------------------------
ALTER TABLE "public"."administration_adminuserprofile" ADD CONSTRAINT "administration_adminuserprofile_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Auto increment value for administration_agentverification
-- ----------------------------
SELECT setval('"public"."administration_agentverification_id_seq"', 1, false);

-- ----------------------------
-- Indexes structure for table administration_agentverification
-- ----------------------------
CREATE INDEX "administrat_est_act_7e932b_idx" ON "public"."administration_agentverification" USING btree (
  "est_actif" "pg_catalog"."bool_ops" ASC NULLS LAST
);
CREATE INDEX "administrat_numero__ff1812_idx" ON "public"."administration_agentverification" USING btree (
  "numero_badge" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);
CREATE INDEX "administrat_zone_af_de4c46_idx" ON "public"."administration_agentverification" USING btree (
  "zone_affectation" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);
CREATE INDEX "administration_agentverification_numero_badge_87284b64_like" ON "public"."administration_agentverification" USING btree (
  "numero_badge" COLLATE "pg_catalog"."default" "pg_catalog"."varchar_pattern_ops" ASC NULLS LAST
);

-- ----------------------------
-- Uniques structure for table administration_agentverification
-- ----------------------------
ALTER TABLE "public"."administration_agentverification" ADD CONSTRAINT "administration_agentverification_numero_badge_key" UNIQUE ("numero_badge");
ALTER TABLE "public"."administration_agentverification" ADD CONSTRAINT "administration_agentverification_user_id_key" UNIQUE ("user_id");

-- ----------------------------
-- Primary Key structure for table administration_agentverification
-- ----------------------------
ALTER TABLE "public"."administration_agentverification" ADD CONSTRAINT "administration_agentverification_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Auto increment value for administration_configurationsysteme
-- ----------------------------
SELECT setval('"public"."administration_configurationsysteme_id_seq"', 1, false);

-- ----------------------------
-- Indexes structure for table administration_configurationsysteme
-- ----------------------------
CREATE INDEX "administrat_cle_75481f_idx" ON "public"."administration_configurationsysteme" USING btree (
  "cle" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);
CREATE INDEX "administrat_est_act_207f5a_idx" ON "public"."administration_configurationsysteme" USING btree (
  "est_actif" "pg_catalog"."bool_ops" ASC NULLS LAST
);
CREATE INDEX "administrat_type_co_44150a_idx" ON "public"."administration_configurationsysteme" USING btree (
  "type_config" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);
CREATE INDEX "administration_configurationsysteme_cle_eed20e01_like" ON "public"."administration_configurationsysteme" USING btree (
  "cle" COLLATE "pg_catalog"."default" "pg_catalog"."varchar_pattern_ops" ASC NULLS LAST
);
CREATE INDEX "administration_configurationsysteme_modifie_par_id_88650061" ON "public"."administration_configurationsysteme" USING btree (
  "modifie_par_id" "pg_catalog"."int4_ops" ASC NULLS LAST
);

-- ----------------------------
-- Uniques structure for table administration_configurationsysteme
-- ----------------------------
ALTER TABLE "public"."administration_configurationsysteme" ADD CONSTRAINT "administration_configurationsysteme_cle_key" UNIQUE ("cle");

-- ----------------------------
-- Primary Key structure for table administration_configurationsysteme
-- ----------------------------
ALTER TABLE "public"."administration_configurationsysteme" ADD CONSTRAINT "administration_configurationsysteme_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Auto increment value for administration_dataversion
-- ----------------------------
SELECT setval('"public"."administration_dataversion_id_seq"', 1, false);

-- ----------------------------
-- Indexes structure for table administration_dataversion
-- ----------------------------
CREATE INDEX "administrat_changed_16e33a_idx" ON "public"."administration_dataversion" USING btree (
  "changed_at" "pg_catalog"."timestamptz_ops" ASC NULLS LAST
);
CREATE INDEX "administrat_content_d6f2c4_idx" ON "public"."administration_dataversion" USING btree (
  "content_type_id" "pg_catalog"."int4_ops" ASC NULLS LAST,
  "object_id" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);
CREATE INDEX "administration_dataversion_changed_by_id_6a46c949" ON "public"."administration_dataversion" USING btree (
  "changed_by_id" "pg_catalog"."int4_ops" ASC NULLS LAST
);
CREATE INDEX "administration_dataversion_content_type_id_4f1d180b" ON "public"."administration_dataversion" USING btree (
  "content_type_id" "pg_catalog"."int4_ops" ASC NULLS LAST
);

-- ----------------------------
-- Uniques structure for table administration_dataversion
-- ----------------------------
ALTER TABLE "public"."administration_dataversion" ADD CONSTRAINT "administration_dataversi_content_type_id_object_i_df94d5f7_uniq" UNIQUE ("content_type_id", "object_id", "version_number");

-- ----------------------------
-- Primary Key structure for table administration_dataversion
-- ----------------------------
ALTER TABLE "public"."administration_dataversion" ADD CONSTRAINT "administration_dataversion_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Auto increment value for administration_permissiongroup
-- ----------------------------
SELECT setval('"public"."administration_permissiongroup_id_seq"', 1, false);

-- ----------------------------
-- Indexes structure for table administration_permissiongroup
-- ----------------------------
CREATE INDEX "administration_permissiongroup_created_by_id_7db6c623" ON "public"."administration_permissiongroup" USING btree (
  "created_by_id" "pg_catalog"."int4_ops" ASC NULLS LAST
);
CREATE INDEX "administration_permissiongroup_name_75958c52_like" ON "public"."administration_permissiongroup" USING btree (
  "name" COLLATE "pg_catalog"."default" "pg_catalog"."varchar_pattern_ops" ASC NULLS LAST
);

-- ----------------------------
-- Uniques structure for table administration_permissiongroup
-- ----------------------------
ALTER TABLE "public"."administration_permissiongroup" ADD CONSTRAINT "administration_permissiongroup_name_key" UNIQUE ("name");

-- ----------------------------
-- Primary Key structure for table administration_permissiongroup
-- ----------------------------
ALTER TABLE "public"."administration_permissiongroup" ADD CONSTRAINT "administration_permissiongroup_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Auto increment value for administration_permissiongroup_users
-- ----------------------------
SELECT setval('"public"."administration_permissiongroup_users_id_seq"', 1, false);

-- ----------------------------
-- Indexes structure for table administration_permissiongroup_users
-- ----------------------------
CREATE INDEX "administration_permissiong_permissiongroup_id_42e3f701" ON "public"."administration_permissiongroup_users" USING btree (
  "permissiongroup_id" "pg_catalog"."int8_ops" ASC NULLS LAST
);
CREATE INDEX "administration_permissiongroup_users_user_id_cccfd414" ON "public"."administration_permissiongroup_users" USING btree (
  "user_id" "pg_catalog"."int4_ops" ASC NULLS LAST
);

-- ----------------------------
-- Uniques structure for table administration_permissiongroup_users
-- ----------------------------
ALTER TABLE "public"."administration_permissiongroup_users" ADD CONSTRAINT "administration_permissio_permissiongroup_id_user__6209a595_uniq" UNIQUE ("permissiongroup_id", "user_id");

-- ----------------------------
-- Primary Key structure for table administration_permissiongroup_users
-- ----------------------------
ALTER TABLE "public"."administration_permissiongroup_users" ADD CONSTRAINT "administration_permissiongroup_users_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Auto increment value for administration_statistiquesplateforme
-- ----------------------------
SELECT setval('"public"."administration_statistiquesplateforme_id_seq"', 1, false);

-- ----------------------------
-- Indexes structure for table administration_statistiquesplateforme
-- ----------------------------
CREATE INDEX "administrat_date_st_edf0c0_idx" ON "public"."administration_statistiquesplateforme" USING btree (
  "date_statistique" "pg_catalog"."date_ops" ASC NULLS LAST
);
CREATE INDEX "administrat_type_st_48ee36_idx" ON "public"."administration_statistiquesplateforme" USING btree (
  "type_statistique" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST,
  "date_statistique" "pg_catalog"."date_ops" ASC NULLS LAST
);

-- ----------------------------
-- Uniques structure for table administration_statistiquesplateforme
-- ----------------------------
ALTER TABLE "public"."administration_statistiquesplateforme" ADD CONSTRAINT "administration_statistiq_type_statistique_date_st_0cae1b01_uniq" UNIQUE ("type_statistique", "date_statistique");

-- ----------------------------
-- Primary Key structure for table administration_statistiquesplateforme
-- ----------------------------
ALTER TABLE "public"."administration_statistiquesplateforme" ADD CONSTRAINT "administration_statistiquesplateforme_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Indexes structure for table administration_verificationqr
-- ----------------------------
CREATE INDEX "administrat_agent_i_ddfb5e_idx" ON "public"."administration_verificationqr" USING btree (
  "agent_id" "pg_catalog"."int8_ops" ASC NULLS LAST
);
CREATE INDEX "administrat_date_ve_1f72a8_idx" ON "public"."administration_verificationqr" USING btree (
  "date_verification" "pg_catalog"."timestamptz_ops" ASC NULLS LAST
);
CREATE INDEX "administrat_qr_code_ee9160_idx" ON "public"."administration_verificationqr" USING btree (
  "qr_code_id" "pg_catalog"."uuid_ops" ASC NULLS LAST
);
CREATE INDEX "administrat_statut__e1389d_idx" ON "public"."administration_verificationqr" USING btree (
  "statut_verification" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);
CREATE INDEX "administration_verificationqr_agent_id_fe3e4c9c" ON "public"."administration_verificationqr" USING btree (
  "agent_id" "pg_catalog"."int8_ops" ASC NULLS LAST
);
CREATE INDEX "administration_verificationqr_qr_code_id_056a7eee" ON "public"."administration_verificationqr" USING btree (
  "qr_code_id" "pg_catalog"."uuid_ops" ASC NULLS LAST
);

-- ----------------------------
-- Primary Key structure for table administration_verificationqr
-- ----------------------------
ALTER TABLE "public"."administration_verificationqr" ADD CONSTRAINT "administration_verificationqr_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Auto increment value for auth_group
-- ----------------------------
SELECT setval('"public"."auth_group_id_seq"', 1, false);

-- ----------------------------
-- Indexes structure for table auth_group
-- ----------------------------
CREATE INDEX "auth_group_name_a6ea08ec_like" ON "public"."auth_group" USING btree (
  "name" COLLATE "pg_catalog"."default" "pg_catalog"."varchar_pattern_ops" ASC NULLS LAST
);

-- ----------------------------
-- Uniques structure for table auth_group
-- ----------------------------
ALTER TABLE "public"."auth_group" ADD CONSTRAINT "auth_group_name_key" UNIQUE ("name");

-- ----------------------------
-- Primary Key structure for table auth_group
-- ----------------------------
ALTER TABLE "public"."auth_group" ADD CONSTRAINT "auth_group_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Auto increment value for auth_group_permissions
-- ----------------------------
SELECT setval('"public"."auth_group_permissions_id_seq"', 1, false);

-- ----------------------------
-- Indexes structure for table auth_group_permissions
-- ----------------------------
CREATE INDEX "auth_group_permissions_group_id_b120cbf9" ON "public"."auth_group_permissions" USING btree (
  "group_id" "pg_catalog"."int4_ops" ASC NULLS LAST
);
CREATE INDEX "auth_group_permissions_permission_id_84c5c92e" ON "public"."auth_group_permissions" USING btree (
  "permission_id" "pg_catalog"."int4_ops" ASC NULLS LAST
);

-- ----------------------------
-- Uniques structure for table auth_group_permissions
-- ----------------------------
ALTER TABLE "public"."auth_group_permissions" ADD CONSTRAINT "auth_group_permissions_group_id_permission_id_0cd325b0_uniq" UNIQUE ("group_id", "permission_id");

-- ----------------------------
-- Primary Key structure for table auth_group_permissions
-- ----------------------------
ALTER TABLE "public"."auth_group_permissions" ADD CONSTRAINT "auth_group_permissions_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Auto increment value for auth_permission
-- ----------------------------
SELECT setval('"public"."auth_permission_id_seq"', 156, true);

-- ----------------------------
-- Indexes structure for table auth_permission
-- ----------------------------
CREATE INDEX "auth_permission_content_type_id_2f476e4b" ON "public"."auth_permission" USING btree (
  "content_type_id" "pg_catalog"."int4_ops" ASC NULLS LAST
);

-- ----------------------------
-- Uniques structure for table auth_permission
-- ----------------------------
ALTER TABLE "public"."auth_permission" ADD CONSTRAINT "auth_permission_content_type_id_codename_01ab375a_uniq" UNIQUE ("content_type_id", "codename");

-- ----------------------------
-- Primary Key structure for table auth_permission
-- ----------------------------
ALTER TABLE "public"."auth_permission" ADD CONSTRAINT "auth_permission_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Auto increment value for auth_user
-- ----------------------------
SELECT setval('"public"."auth_user_id_seq"', 19, true);

-- ----------------------------
-- Indexes structure for table auth_user
-- ----------------------------
CREATE INDEX "auth_user_username_6821ab7c_like" ON "public"."auth_user" USING btree (
  "username" COLLATE "pg_catalog"."default" "pg_catalog"."varchar_pattern_ops" ASC NULLS LAST
);

-- ----------------------------
-- Uniques structure for table auth_user
-- ----------------------------
ALTER TABLE "public"."auth_user" ADD CONSTRAINT "auth_user_username_key" UNIQUE ("username");

-- ----------------------------
-- Primary Key structure for table auth_user
-- ----------------------------
ALTER TABLE "public"."auth_user" ADD CONSTRAINT "auth_user_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Auto increment value for auth_user_groups
-- ----------------------------
SELECT setval('"public"."auth_user_groups_id_seq"', 1, false);

-- ----------------------------
-- Indexes structure for table auth_user_groups
-- ----------------------------
CREATE INDEX "auth_user_groups_group_id_97559544" ON "public"."auth_user_groups" USING btree (
  "group_id" "pg_catalog"."int4_ops" ASC NULLS LAST
);
CREATE INDEX "auth_user_groups_user_id_6a12ed8b" ON "public"."auth_user_groups" USING btree (
  "user_id" "pg_catalog"."int4_ops" ASC NULLS LAST
);

-- ----------------------------
-- Uniques structure for table auth_user_groups
-- ----------------------------
ALTER TABLE "public"."auth_user_groups" ADD CONSTRAINT "auth_user_groups_user_id_group_id_94350c0c_uniq" UNIQUE ("user_id", "group_id");

-- ----------------------------
-- Primary Key structure for table auth_user_groups
-- ----------------------------
ALTER TABLE "public"."auth_user_groups" ADD CONSTRAINT "auth_user_groups_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Auto increment value for auth_user_user_permissions
-- ----------------------------
SELECT setval('"public"."auth_user_user_permissions_id_seq"', 1, false);

-- ----------------------------
-- Indexes structure for table auth_user_user_permissions
-- ----------------------------
CREATE INDEX "auth_user_user_permissions_permission_id_1fbb5f2c" ON "public"."auth_user_user_permissions" USING btree (
  "permission_id" "pg_catalog"."int4_ops" ASC NULLS LAST
);
CREATE INDEX "auth_user_user_permissions_user_id_a95ead1b" ON "public"."auth_user_user_permissions" USING btree (
  "user_id" "pg_catalog"."int4_ops" ASC NULLS LAST
);

-- ----------------------------
-- Uniques structure for table auth_user_user_permissions
-- ----------------------------
ALTER TABLE "public"."auth_user_user_permissions" ADD CONSTRAINT "auth_user_user_permissions_user_id_permission_id_14a6b632_uniq" UNIQUE ("user_id", "permission_id");

-- ----------------------------
-- Primary Key structure for table auth_user_user_permissions
-- ----------------------------
ALTER TABLE "public"."auth_user_user_permissions" ADD CONSTRAINT "auth_user_user_permissions_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Indexes structure for table core_auditlog
-- ----------------------------
CREATE INDEX "core_auditl_action_57cfb7_idx" ON "public"."core_auditlog" USING btree (
  "action" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST,
  "date_action" "pg_catalog"."timestamptz_ops" ASC NULLS LAST
);
CREATE INDEX "core_auditl_table_c_7cd977_idx" ON "public"."core_auditlog" USING btree (
  "table_concernee" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST,
  "objet_id" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);
CREATE INDEX "core_auditl_user_id_4c17f9_idx" ON "public"."core_auditlog" USING btree (
  "user_id" "pg_catalog"."int4_ops" ASC NULLS LAST,
  "date_action" "pg_catalog"."timestamptz_ops" ASC NULLS LAST
);
CREATE INDEX "core_auditlog_user_id_3797aaab" ON "public"."core_auditlog" USING btree (
  "user_id" "pg_catalog"."int4_ops" ASC NULLS LAST
);

-- ----------------------------
-- Primary Key structure for table core_auditlog
-- ----------------------------
ALTER TABLE "public"."core_auditlog" ADD CONSTRAINT "core_auditlog_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Indexes structure for table core_companyprofile
-- ----------------------------
CREATE INDEX "core_compan_company_11108b_idx" ON "public"."core_companyprofile" USING btree (
  "company_name" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);
CREATE INDEX "core_compan_tax_id_8c1062_idx" ON "public"."core_companyprofile" USING btree (
  "tax_id" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);
CREATE INDEX "core_companyprofile_tax_id_745690b1_like" ON "public"."core_companyprofile" USING btree (
  "tax_id" COLLATE "pg_catalog"."default" "pg_catalog"."varchar_pattern_ops" ASC NULLS LAST
);

-- ----------------------------
-- Uniques structure for table core_companyprofile
-- ----------------------------
ALTER TABLE "public"."core_companyprofile" ADD CONSTRAINT "core_companyprofile_tax_id_key" UNIQUE ("tax_id");
ALTER TABLE "public"."core_companyprofile" ADD CONSTRAINT "core_companyprofile_user_profile_id_key" UNIQUE ("user_profile_id");

-- ----------------------------
-- Primary Key structure for table core_companyprofile
-- ----------------------------
ALTER TABLE "public"."core_companyprofile" ADD CONSTRAINT "core_companyprofile_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Uniques structure for table core_emergencyserviceprofile
-- ----------------------------
ALTER TABLE "public"."core_emergencyserviceprofile" ADD CONSTRAINT "core_emergencyserviceprofile_user_profile_id_key" UNIQUE ("user_profile_id");

-- ----------------------------
-- Primary Key structure for table core_emergencyserviceprofile
-- ----------------------------
ALTER TABLE "public"."core_emergencyserviceprofile" ADD CONSTRAINT "core_emergencyserviceprofile_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Indexes structure for table core_entrepriseprofile
-- ----------------------------
CREATE INDEX "core_entrep_nom_ent_e47073_idx" ON "public"."core_entrepriseprofile" USING btree (
  "nom_entreprise" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);
CREATE INDEX "core_entrep_numero__b9836e_idx" ON "public"."core_entrepriseprofile" USING btree (
  "numero_contribuable" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);
CREATE INDEX "core_entrepriseprofile_numero_contribuable_2775395c_like" ON "public"."core_entrepriseprofile" USING btree (
  "numero_contribuable" COLLATE "pg_catalog"."default" "pg_catalog"."varchar_pattern_ops" ASC NULLS LAST
);

-- ----------------------------
-- Uniques structure for table core_entrepriseprofile
-- ----------------------------
ALTER TABLE "public"."core_entrepriseprofile" ADD CONSTRAINT "core_entrepriseprofile_numero_contribuable_key" UNIQUE ("numero_contribuable");
ALTER TABLE "public"."core_entrepriseprofile" ADD CONSTRAINT "core_entrepriseprofile_user_id_key" UNIQUE ("user_id");

-- ----------------------------
-- Primary Key structure for table core_entrepriseprofile
-- ----------------------------
ALTER TABLE "public"."core_entrepriseprofile" ADD CONSTRAINT "core_entrepriseprofile_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Uniques structure for table core_governmentadminprofile
-- ----------------------------
ALTER TABLE "public"."core_governmentadminprofile" ADD CONSTRAINT "core_governmentadminprofile_user_profile_id_key" UNIQUE ("user_profile_id");

-- ----------------------------
-- Primary Key structure for table core_governmentadminprofile
-- ----------------------------
ALTER TABLE "public"."core_governmentadminprofile" ADD CONSTRAINT "core_governmentadminprofile_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Uniques structure for table core_individualprofile
-- ----------------------------
ALTER TABLE "public"."core_individualprofile" ADD CONSTRAINT "core_individualprofile_user_profile_id_key" UNIQUE ("user_profile_id");

-- ----------------------------
-- Primary Key structure for table core_individualprofile
-- ----------------------------
ALTER TABLE "public"."core_individualprofile" ADD CONSTRAINT "core_individualprofile_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Indexes structure for table core_lawenforcementprofile
-- ----------------------------
CREATE INDEX "core_lawenf_badge_n_61b95c_idx" ON "public"."core_lawenforcementprofile" USING btree (
  "badge_number" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);
CREATE INDEX "core_lawenforcementprofile_badge_number_29571a73_like" ON "public"."core_lawenforcementprofile" USING btree (
  "badge_number" COLLATE "pg_catalog"."default" "pg_catalog"."varchar_pattern_ops" ASC NULLS LAST
);

-- ----------------------------
-- Uniques structure for table core_lawenforcementprofile
-- ----------------------------
ALTER TABLE "public"."core_lawenforcementprofile" ADD CONSTRAINT "core_lawenforcementprofile_badge_number_key" UNIQUE ("badge_number");
ALTER TABLE "public"."core_lawenforcementprofile" ADD CONSTRAINT "core_lawenforcementprofile_user_profile_id_key" UNIQUE ("user_profile_id");

-- ----------------------------
-- Primary Key structure for table core_lawenforcementprofile
-- ----------------------------
ALTER TABLE "public"."core_lawenforcementprofile" ADD CONSTRAINT "core_lawenforcementprofile_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Indexes structure for table core_userprofile
-- ----------------------------
CREATE INDEX "core_userpr_est_ent_3bda08_idx" ON "public"."core_userprofile" USING btree (
  "est_entreprise" "pg_catalog"."bool_ops" ASC NULLS LAST
);
CREATE INDEX "core_userpr_telepho_ee0e58_idx" ON "public"."core_userprofile" USING btree (
  "telephone" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);
CREATE INDEX "core_userpr_user_ty_baccfd_idx" ON "public"."core_userprofile" USING btree (
  "user_type" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);
CREATE INDEX "core_userpr_verific_9ab6af_idx" ON "public"."core_userprofile" USING btree (
  "verification_status" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);

-- ----------------------------
-- Uniques structure for table core_userprofile
-- ----------------------------
ALTER TABLE "public"."core_userprofile" ADD CONSTRAINT "core_userprofile_user_id_key" UNIQUE ("user_id");

-- ----------------------------
-- Primary Key structure for table core_userprofile
-- ----------------------------
ALTER TABLE "public"."core_userprofile" ADD CONSTRAINT "core_userprofile_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Indexes structure for table core_verificationdocument
-- ----------------------------
CREATE INDEX "core_verifi_documen_ac55b2_idx" ON "public"."core_verificationdocument" USING btree (
  "document_type" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);
CREATE INDEX "core_verifi_verific_3a7150_idx" ON "public"."core_verificationdocument" USING btree (
  "verification_status" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);
CREATE INDEX "core_verificationdocument_user_profile_id_e5c0fbfe" ON "public"."core_verificationdocument" USING btree (
  "user_profile_id" "pg_catalog"."uuid_ops" ASC NULLS LAST
);
CREATE INDEX "core_verificationdocument_verified_by_id_b278dd82" ON "public"."core_verificationdocument" USING btree (
  "verified_by_id" "pg_catalog"."int4_ops" ASC NULLS LAST
);

-- ----------------------------
-- Primary Key structure for table core_verificationdocument
-- ----------------------------
ALTER TABLE "public"."core_verificationdocument" ADD CONSTRAINT "core_verificationdocument_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Auto increment value for django_admin_log
-- ----------------------------
SELECT setval('"public"."django_admin_log_id_seq"', 1, false);

-- ----------------------------
-- Indexes structure for table django_admin_log
-- ----------------------------
CREATE INDEX "django_admin_log_content_type_id_c4bce8eb" ON "public"."django_admin_log" USING btree (
  "content_type_id" "pg_catalog"."int4_ops" ASC NULLS LAST
);
CREATE INDEX "django_admin_log_user_id_c564eba6" ON "public"."django_admin_log" USING btree (
  "user_id" "pg_catalog"."int4_ops" ASC NULLS LAST
);

-- ----------------------------
-- Checks structure for table django_admin_log
-- ----------------------------
ALTER TABLE "public"."django_admin_log" ADD CONSTRAINT "django_admin_log_action_flag_check" CHECK (action_flag >= 0);

-- ----------------------------
-- Primary Key structure for table django_admin_log
-- ----------------------------
ALTER TABLE "public"."django_admin_log" ADD CONSTRAINT "django_admin_log_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Auto increment value for django_content_type
-- ----------------------------
SELECT setval('"public"."django_content_type_id_seq"', 39, true);

-- ----------------------------
-- Uniques structure for table django_content_type
-- ----------------------------
ALTER TABLE "public"."django_content_type" ADD CONSTRAINT "django_content_type_app_label_model_76bd3d3b_uniq" UNIQUE ("app_label", "model");

-- ----------------------------
-- Primary Key structure for table django_content_type
-- ----------------------------
ALTER TABLE "public"."django_content_type" ADD CONSTRAINT "django_content_type_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Auto increment value for django_migrations
-- ----------------------------
SELECT setval('"public"."django_migrations_id_seq"', 51, true);

-- ----------------------------
-- Primary Key structure for table django_migrations
-- ----------------------------
ALTER TABLE "public"."django_migrations" ADD CONSTRAINT "django_migrations_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Indexes structure for table django_session
-- ----------------------------
CREATE INDEX "django_session_expire_date_a5c62663" ON "public"."django_session" USING btree (
  "expire_date" "pg_catalog"."timestamptz_ops" ASC NULLS LAST
);
CREATE INDEX "django_session_session_key_c0390e0f_like" ON "public"."django_session" USING btree (
  "session_key" COLLATE "pg_catalog"."default" "pg_catalog"."varchar_pattern_ops" ASC NULLS LAST
);

-- ----------------------------
-- Primary Key structure for table django_session
-- ----------------------------
ALTER TABLE "public"."django_session" ADD CONSTRAINT "django_session_pkey" PRIMARY KEY ("session_key");

-- ----------------------------
-- Auto increment value for django_site
-- ----------------------------
SELECT setval('"public"."django_site_id_seq"', 1, true);

-- ----------------------------
-- Indexes structure for table django_site
-- ----------------------------
CREATE INDEX "django_site_domain_a2e37b91_like" ON "public"."django_site" USING btree (
  "domain" COLLATE "pg_catalog"."default" "pg_catalog"."varchar_pattern_ops" ASC NULLS LAST
);

-- ----------------------------
-- Uniques structure for table django_site
-- ----------------------------
ALTER TABLE "public"."django_site" ADD CONSTRAINT "django_site_domain_a2e37b91_uniq" UNIQUE ("domain");

-- ----------------------------
-- Primary Key structure for table django_site
-- ----------------------------
ALTER TABLE "public"."django_site" ADD CONSTRAINT "django_site_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Indexes structure for table notifications_notification
-- ----------------------------
CREATE INDEX "notif_user_non_lue_idx" ON "public"."notifications_notification" USING btree (
  "user_id" "pg_catalog"."int4_ops" ASC NULLS LAST,
  "est_lue" "pg_catalog"."bool_ops" ASC NULLS LAST
) WHERE NOT est_lue;
CREATE INDEX "notificatio_date_en_1a8f7a_idx" ON "public"."notifications_notification" USING btree (
  "date_envoi" "pg_catalog"."timestamptz_ops" ASC NULLS LAST
);
CREATE INDEX "notificatio_type_no_ba8ea8_idx" ON "public"."notifications_notification" USING btree (
  "type_notification" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);
CREATE INDEX "notificatio_user_id_c291d5_idx" ON "public"."notifications_notification" USING btree (
  "user_id" "pg_catalog"."int4_ops" ASC NULLS LAST
);
CREATE INDEX "notifications_notification_user_id_b5e8c0ff" ON "public"."notifications_notification" USING btree (
  "user_id" "pg_catalog"."int4_ops" ASC NULLS LAST
);

-- ----------------------------
-- Checks structure for table notifications_notification
-- ----------------------------
ALTER TABLE "public"."notifications_notification" ADD CONSTRAINT "date_lecture_after_envoi" CHECK (date_lecture IS NULL OR date_lecture >= date_envoi);

-- ----------------------------
-- Primary Key structure for table notifications_notification
-- ----------------------------
ALTER TABLE "public"."notifications_notification" ADD CONSTRAINT "notifications_notification_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Auto increment value for notifications_notificationtemplate
-- ----------------------------
SELECT setval('"public"."notifications_notificationtemplate_id_seq"', 1, false);

-- ----------------------------
-- Indexes structure for table notifications_notificationtemplate
-- ----------------------------
CREATE INDEX "notificatio_type_te_bb1951_idx" ON "public"."notifications_notificationtemplate" USING btree (
  "type_template" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST,
  "langue" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST,
  "est_actif" "pg_catalog"."bool_ops" ASC NULLS LAST
);

-- ----------------------------
-- Uniques structure for table notifications_notificationtemplate
-- ----------------------------
ALTER TABLE "public"."notifications_notificationtemplate" ADD CONSTRAINT "notifications_notificati_type_template_langue_17ec3c74_uniq" UNIQUE ("type_template", "langue");

-- ----------------------------
-- Primary Key structure for table notifications_notificationtemplate
-- ----------------------------
ALTER TABLE "public"."notifications_notificationtemplate" ADD CONSTRAINT "notifications_notificationtemplate_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Indexes structure for table payments_paiementtaxe
-- ----------------------------
CREATE INDEX "payments_pa_date_pa_895dff_idx" ON "public"."payments_paiementtaxe" USING btree (
  "date_paiement" "pg_catalog"."timestamptz_ops" ASC NULLS LAST
);
CREATE INDEX "payments_pa_statut_a39adc_idx" ON "public"."payments_paiementtaxe" USING btree (
  "statut" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);
CREATE INDEX "payments_pa_stripe__34d8df_idx" ON "public"."payments_paiementtaxe" USING btree (
  "stripe_status" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);
CREATE INDEX "payments_pa_stripe__5351b1_idx" ON "public"."payments_paiementtaxe" USING btree (
  "stripe_payment_intent_id" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);
CREATE INDEX "payments_pa_transac_408778_idx" ON "public"."payments_paiementtaxe" USING btree (
  "transaction_id" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);
CREATE INDEX "payments_pa_vehicul_bac3be_idx" ON "public"."payments_paiementtaxe" USING btree (
  "vehicule_plaque_id" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST,
  "annee_fiscale" "pg_catalog"."int4_ops" ASC NULLS LAST
);
CREATE INDEX "payments_paiementtaxe_stripe_payment_intent_id_2ffe8700_like" ON "public"."payments_paiementtaxe" USING btree (
  "stripe_payment_intent_id" COLLATE "pg_catalog"."default" "pg_catalog"."varchar_pattern_ops" ASC NULLS LAST
);
CREATE INDEX "payments_paiementtaxe_transaction_id_f6c0ba15_like" ON "public"."payments_paiementtaxe" USING btree (
  "transaction_id" COLLATE "pg_catalog"."default" "pg_catalog"."varchar_pattern_ops" ASC NULLS LAST
);
CREATE INDEX "payments_paiementtaxe_vehicule_plaque_id_50717892" ON "public"."payments_paiementtaxe" USING btree (
  "vehicule_plaque_id" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);
CREATE INDEX "payments_paiementtaxe_vehicule_plaque_id_50717892_like" ON "public"."payments_paiementtaxe" USING btree (
  "vehicule_plaque_id" COLLATE "pg_catalog"."default" "pg_catalog"."varchar_pattern_ops" ASC NULLS LAST
);

-- ----------------------------
-- Uniques structure for table payments_paiementtaxe
-- ----------------------------
ALTER TABLE "public"."payments_paiementtaxe" ADD CONSTRAINT "payments_paiementtaxe_transaction_id_key" UNIQUE ("transaction_id");
ALTER TABLE "public"."payments_paiementtaxe" ADD CONSTRAINT "payments_paiementtaxe_vehicule_plaque_id_annee_fac0fb4d_uniq" UNIQUE ("vehicule_plaque_id", "annee_fiscale");
ALTER TABLE "public"."payments_paiementtaxe" ADD CONSTRAINT "payments_paiementtaxe_stripe_payment_intent_id_key" UNIQUE ("stripe_payment_intent_id");

-- ----------------------------
-- Checks structure for table payments_paiementtaxe
-- ----------------------------
ALTER TABLE "public"."payments_paiementtaxe" ADD CONSTRAINT "payments_paiementtaxe_annee_fiscale_check" CHECK (annee_fiscale >= 0);

-- ----------------------------
-- Primary Key structure for table payments_paiementtaxe
-- ----------------------------
ALTER TABLE "public"."payments_paiementtaxe" ADD CONSTRAINT "payments_paiementtaxe_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Indexes structure for table payments_qrcode
-- ----------------------------
CREATE INDEX "payments_qr_vehicul_38803b_idx" ON "public"."payments_qrcode" USING btree (
  "vehicule_plaque_id" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST,
  "annee_fiscale" "pg_catalog"."int4_ops" ASC NULLS LAST
);
CREATE INDEX "payments_qrcode_token_48caf1a3_like" ON "public"."payments_qrcode" USING btree (
  "token" COLLATE "pg_catalog"."default" "pg_catalog"."varchar_pattern_ops" ASC NULLS LAST
);
CREATE INDEX "payments_qrcode_vehicule_plaque_id_f9a46c70" ON "public"."payments_qrcode" USING btree (
  "vehicule_plaque_id" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);
CREATE INDEX "payments_qrcode_vehicule_plaque_id_f9a46c70_like" ON "public"."payments_qrcode" USING btree (
  "vehicule_plaque_id" COLLATE "pg_catalog"."default" "pg_catalog"."varchar_pattern_ops" ASC NULLS LAST
);
CREATE INDEX "qr_expiration_actif_idx" ON "public"."payments_qrcode" USING btree (
  "date_expiration" "pg_catalog"."timestamptz_ops" ASC NULLS LAST
) WHERE est_actif;
CREATE INDEX "qr_token_actif_idx" ON "public"."payments_qrcode" USING btree (
  "token" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
) WHERE est_actif;

-- ----------------------------
-- Uniques structure for table payments_qrcode
-- ----------------------------
ALTER TABLE "public"."payments_qrcode" ADD CONSTRAINT "payments_qrcode_token_key" UNIQUE ("token");
ALTER TABLE "public"."payments_qrcode" ADD CONSTRAINT "payments_qrcode_vehicule_plaque_id_annee_fiscale_cf4283d8_uniq" UNIQUE ("vehicule_plaque_id", "annee_fiscale");

-- ----------------------------
-- Checks structure for table payments_qrcode
-- ----------------------------
ALTER TABLE "public"."payments_qrcode" ADD CONSTRAINT "payments_qrcode_annee_fiscale_check" CHECK (annee_fiscale >= 0);
ALTER TABLE "public"."payments_qrcode" ADD CONSTRAINT "payments_qrcode_nombre_scans_check" CHECK (nombre_scans >= 0);

-- ----------------------------
-- Primary Key structure for table payments_qrcode
-- ----------------------------
ALTER TABLE "public"."payments_qrcode" ADD CONSTRAINT "payments_qrcode_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Auto increment value for payments_stripeconfig
-- ----------------------------
SELECT setval('"public"."payments_stripeconfig_id_seq"', 1, false);

-- ----------------------------
-- Indexes structure for table payments_stripeconfig
-- ----------------------------
CREATE INDEX "payments_stripeconfig_environment_f179f8bd_like" ON "public"."payments_stripeconfig" USING btree (
  "environment" COLLATE "pg_catalog"."default" "pg_catalog"."varchar_pattern_ops" ASC NULLS LAST
);

-- ----------------------------
-- Uniques structure for table payments_stripeconfig
-- ----------------------------
ALTER TABLE "public"."payments_stripeconfig" ADD CONSTRAINT "payments_stripeconfig_environment_key" UNIQUE ("environment");

-- ----------------------------
-- Primary Key structure for table payments_stripeconfig
-- ----------------------------
ALTER TABLE "public"."payments_stripeconfig" ADD CONSTRAINT "payments_stripeconfig_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Auto increment value for payments_stripewebhookevent
-- ----------------------------
SELECT setval('"public"."payments_stripewebhookevent_id_seq"', 1, false);

-- ----------------------------
-- Indexes structure for table payments_stripewebhookevent
-- ----------------------------
CREATE INDEX "payments_stripewebhookevent_stripe_event_id_903fa3a3_like" ON "public"."payments_stripewebhookevent" USING btree (
  "stripe_event_id" COLLATE "pg_catalog"."default" "pg_catalog"."varchar_pattern_ops" ASC NULLS LAST
);

-- ----------------------------
-- Uniques structure for table payments_stripewebhookevent
-- ----------------------------
ALTER TABLE "public"."payments_stripewebhookevent" ADD CONSTRAINT "payments_stripewebhookevent_stripe_event_id_key" UNIQUE ("stripe_event_id");

-- ----------------------------
-- Primary Key structure for table payments_stripewebhookevent
-- ----------------------------
ALTER TABLE "public"."payments_stripewebhookevent" ADD CONSTRAINT "payments_stripewebhookevent_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Auto increment value for socialaccount_socialaccount
-- ----------------------------
SELECT setval('"public"."socialaccount_socialaccount_id_seq"', 1, false);

-- ----------------------------
-- Indexes structure for table socialaccount_socialaccount
-- ----------------------------
CREATE INDEX "socialaccount_socialaccount_user_id_8146e70c" ON "public"."socialaccount_socialaccount" USING btree (
  "user_id" "pg_catalog"."int4_ops" ASC NULLS LAST
);

-- ----------------------------
-- Uniques structure for table socialaccount_socialaccount
-- ----------------------------
ALTER TABLE "public"."socialaccount_socialaccount" ADD CONSTRAINT "socialaccount_socialaccount_provider_uid_fc810c6e_uniq" UNIQUE ("provider", "uid");

-- ----------------------------
-- Primary Key structure for table socialaccount_socialaccount
-- ----------------------------
ALTER TABLE "public"."socialaccount_socialaccount" ADD CONSTRAINT "socialaccount_socialaccount_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Auto increment value for socialaccount_socialapp
-- ----------------------------
SELECT setval('"public"."socialaccount_socialapp_id_seq"', 1, false);

-- ----------------------------
-- Primary Key structure for table socialaccount_socialapp
-- ----------------------------
ALTER TABLE "public"."socialaccount_socialapp" ADD CONSTRAINT "socialaccount_socialapp_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Auto increment value for socialaccount_socialapp_sites
-- ----------------------------
SELECT setval('"public"."socialaccount_socialapp_sites_id_seq"', 1, false);

-- ----------------------------
-- Indexes structure for table socialaccount_socialapp_sites
-- ----------------------------
CREATE INDEX "socialaccount_socialapp_sites_site_id_2579dee5" ON "public"."socialaccount_socialapp_sites" USING btree (
  "site_id" "pg_catalog"."int4_ops" ASC NULLS LAST
);
CREATE INDEX "socialaccount_socialapp_sites_socialapp_id_97fb6e7d" ON "public"."socialaccount_socialapp_sites" USING btree (
  "socialapp_id" "pg_catalog"."int4_ops" ASC NULLS LAST
);

-- ----------------------------
-- Uniques structure for table socialaccount_socialapp_sites
-- ----------------------------
ALTER TABLE "public"."socialaccount_socialapp_sites" ADD CONSTRAINT "socialaccount_socialapp__socialapp_id_site_id_71a9a768_uniq" UNIQUE ("socialapp_id", "site_id");

-- ----------------------------
-- Primary Key structure for table socialaccount_socialapp_sites
-- ----------------------------
ALTER TABLE "public"."socialaccount_socialapp_sites" ADD CONSTRAINT "socialaccount_socialapp_sites_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Auto increment value for socialaccount_socialtoken
-- ----------------------------
SELECT setval('"public"."socialaccount_socialtoken_id_seq"', 1, false);

-- ----------------------------
-- Indexes structure for table socialaccount_socialtoken
-- ----------------------------
CREATE INDEX "socialaccount_socialtoken_account_id_951f210e" ON "public"."socialaccount_socialtoken" USING btree (
  "account_id" "pg_catalog"."int4_ops" ASC NULLS LAST
);
CREATE INDEX "socialaccount_socialtoken_app_id_636a42d7" ON "public"."socialaccount_socialtoken" USING btree (
  "app_id" "pg_catalog"."int4_ops" ASC NULLS LAST
);

-- ----------------------------
-- Uniques structure for table socialaccount_socialtoken
-- ----------------------------
ALTER TABLE "public"."socialaccount_socialtoken" ADD CONSTRAINT "socialaccount_socialtoken_app_id_account_id_fca4e0ac_uniq" UNIQUE ("app_id", "account_id");

-- ----------------------------
-- Primary Key structure for table socialaccount_socialtoken
-- ----------------------------
ALTER TABLE "public"."socialaccount_socialtoken" ADD CONSTRAINT "socialaccount_socialtoken_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Indexes structure for table vehicles_documentvehicule
-- ----------------------------
CREATE INDEX "vehicles_do_documen_f27503_idx" ON "public"."vehicles_documentvehicule" USING btree (
  "document_type" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);
CREATE INDEX "vehicles_do_vehicul_1d12d6_idx" ON "public"."vehicles_documentvehicule" USING btree (
  "vehicule_id" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);
CREATE INDEX "vehicles_do_verific_8b169b_idx" ON "public"."vehicles_documentvehicule" USING btree (
  "verification_status" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);
CREATE INDEX "vehicles_documentvehicule_uploaded_by_id_5f48f22c" ON "public"."vehicles_documentvehicule" USING btree (
  "uploaded_by_id" "pg_catalog"."int4_ops" ASC NULLS LAST
);
CREATE INDEX "vehicles_documentvehicule_vehicule_id_f06206b9" ON "public"."vehicles_documentvehicule" USING btree (
  "vehicule_id" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);
CREATE INDEX "vehicles_documentvehicule_vehicule_id_f06206b9_like" ON "public"."vehicles_documentvehicule" USING btree (
  "vehicule_id" COLLATE "pg_catalog"."default" "pg_catalog"."varchar_pattern_ops" ASC NULLS LAST
);

-- ----------------------------
-- Primary Key structure for table vehicles_documentvehicule
-- ----------------------------
ALTER TABLE "public"."vehicles_documentvehicule" ADD CONSTRAINT "vehicles_documentvehicule_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Auto increment value for vehicles_grilletarifaire
-- ----------------------------
SELECT setval('"public"."vehicles_grilletarifaire_id_seq"', 96, true);

-- ----------------------------
-- Indexes structure for table vehicles_grilletarifaire
-- ----------------------------
CREATE INDEX "vehicles_gr_annee_f_2aced1_idx" ON "public"."vehicles_grilletarifaire" USING btree (
  "annee_fiscale" "pg_catalog"."int4_ops" ASC NULLS LAST,
  "est_active" "pg_catalog"."bool_ops" ASC NULLS LAST
);
CREATE INDEX "vehicles_gr_puissan_e47476_idx" ON "public"."vehicles_grilletarifaire" USING btree (
  "puissance_min_cv" "pg_catalog"."int4_ops" ASC NULLS LAST,
  "puissance_max_cv" "pg_catalog"."int4_ops" ASC NULLS LAST,
  "source_energie" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);

-- ----------------------------
-- Uniques structure for table vehicles_grilletarifaire
-- ----------------------------
ALTER TABLE "public"."vehicles_grilletarifaire" ADD CONSTRAINT "vehicles_grilletarifaire_puissance_min_cv_puissan_eea4cd0d_uniq" UNIQUE ("puissance_min_cv", "puissance_max_cv", "source_energie", "age_min_annees", "age_max_annees", "annee_fiscale");

-- ----------------------------
-- Checks structure for table vehicles_grilletarifaire
-- ----------------------------
ALTER TABLE "public"."vehicles_grilletarifaire" ADD CONSTRAINT "vehicles_grilletarifaire_age_min_annees_check" CHECK (age_min_annees >= 0);
ALTER TABLE "public"."vehicles_grilletarifaire" ADD CONSTRAINT "vehicles_grilletarifaire_puissance_min_cv_check" CHECK (puissance_min_cv >= 0);
ALTER TABLE "public"."vehicles_grilletarifaire" ADD CONSTRAINT "vehicles_grilletarifaire_annee_fiscale_check" CHECK (annee_fiscale >= 0);
ALTER TABLE "public"."vehicles_grilletarifaire" ADD CONSTRAINT "vehicles_grilletarifaire_age_max_annees_check" CHECK (age_max_annees >= 0);
ALTER TABLE "public"."vehicles_grilletarifaire" ADD CONSTRAINT "vehicles_grilletarifaire_puissance_max_cv_check" CHECK (puissance_max_cv >= 0);

-- ----------------------------
-- Primary Key structure for table vehicles_grilletarifaire
-- ----------------------------
ALTER TABLE "public"."vehicles_grilletarifaire" ADD CONSTRAINT "vehicles_grilletarifaire_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Auto increment value for vehicles_vehicletype
-- ----------------------------
SELECT setval('"public"."vehicles_vehicletype_id_seq"', 7, true);

-- ----------------------------
-- Indexes structure for table vehicles_vehicletype
-- ----------------------------
CREATE INDEX "vehicles_ve_est_act_869b75_idx" ON "public"."vehicles_vehicletype" USING btree (
  "est_actif" "pg_catalog"."bool_ops" ASC NULLS LAST
);
CREATE INDEX "vehicles_ve_ordre_a_e4a324_idx" ON "public"."vehicles_vehicletype" USING btree (
  "ordre_affichage" "pg_catalog"."int4_ops" ASC NULLS LAST
);
CREATE INDEX "vehicles_vehicletype_nom_65a4eac3_like" ON "public"."vehicles_vehicletype" USING btree (
  "nom" COLLATE "pg_catalog"."default" "pg_catalog"."varchar_pattern_ops" ASC NULLS LAST
);

-- ----------------------------
-- Uniques structure for table vehicles_vehicletype
-- ----------------------------
ALTER TABLE "public"."vehicles_vehicletype" ADD CONSTRAINT "vehicles_vehicletype_nom_key" UNIQUE ("nom");

-- ----------------------------
-- Checks structure for table vehicles_vehicletype
-- ----------------------------
ALTER TABLE "public"."vehicles_vehicletype" ADD CONSTRAINT "vehicles_vehicletype_ordre_affichage_check" CHECK (ordre_affichage >= 0);

-- ----------------------------
-- Primary Key structure for table vehicles_vehicletype
-- ----------------------------
ALTER TABLE "public"."vehicles_vehicletype" ADD CONSTRAINT "vehicles_vehicletype_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Indexes structure for table vehicles_vehicule
-- ----------------------------
CREATE INDEX "vehicles_ve_categor_0f5990_idx" ON "public"."vehicles_vehicule" USING btree (
  "categorie_vehicule" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);
CREATE INDEX "vehicles_ve_proprie_0798fa_idx" ON "public"."vehicles_vehicule" USING btree (
  "proprietaire_id" "pg_catalog"."int4_ops" ASC NULLS LAST
);
CREATE INDEX "vehicles_ve_puissan_fe358b_idx" ON "public"."vehicles_vehicule" USING btree (
  "puissance_fiscale_cv" "pg_catalog"."int4_ops" ASC NULLS LAST
);
CREATE INDEX "vehicles_ve_source__0e6e46_idx" ON "public"."vehicles_vehicule" USING btree (
  "source_energie" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);
CREATE INDEX "vehicles_ve_type_ve_80f00e_idx" ON "public"."vehicles_vehicule" USING btree (
  "type_vehicule_id" "pg_catalog"."int8_ops" ASC NULLS LAST
);
CREATE INDEX "vehicles_vehicule_plaque_immatriculation_674f1f0f_like" ON "public"."vehicles_vehicule" USING btree (
  "plaque_immatriculation" COLLATE "pg_catalog"."default" "pg_catalog"."varchar_pattern_ops" ASC NULLS LAST
);
CREATE INDEX "vehicles_vehicule_proprietaire_id_71bf2b83" ON "public"."vehicles_vehicule" USING btree (
  "proprietaire_id" "pg_catalog"."int4_ops" ASC NULLS LAST
);
CREATE INDEX "vehicles_vehicule_type_vehicule_id_c51f9ee7" ON "public"."vehicles_vehicule" USING btree (
  "type_vehicule_id" "pg_catalog"."int8_ops" ASC NULLS LAST
);

-- ----------------------------
-- Checks structure for table vehicles_vehicule
-- ----------------------------
ALTER TABLE "public"."vehicles_vehicule" ADD CONSTRAINT "vehicles_vehicule_puissance_fiscale_cv_check" CHECK (puissance_fiscale_cv >= 0);
ALTER TABLE "public"."vehicles_vehicule" ADD CONSTRAINT "vehicles_vehicule_cylindree_cm3_check" CHECK (cylindree_cm3 >= 0);

-- ----------------------------
-- Primary Key structure for table vehicles_vehicule
-- ----------------------------
ALTER TABLE "public"."vehicles_vehicule" ADD CONSTRAINT "vehicles_vehicule_pkey" PRIMARY KEY ("plaque_immatriculation");

-- ----------------------------
-- Foreign Keys structure for table account_emailaddress
-- ----------------------------
ALTER TABLE "public"."account_emailaddress" ADD CONSTRAINT "account_emailaddress_user_id_2c513194_fk_auth_user_id" FOREIGN KEY ("user_id") REFERENCES "public"."auth_user" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION DEFERRABLE INITIALLY DEFERRED;

-- ----------------------------
-- Foreign Keys structure for table account_emailconfirmation
-- ----------------------------
ALTER TABLE "public"."account_emailconfirmation" ADD CONSTRAINT "account_emailconfirm_email_address_id_5b7f8c58_fk_account_e" FOREIGN KEY ("email_address_id") REFERENCES "public"."account_emailaddress" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION DEFERRABLE INITIALLY DEFERRED;

-- ----------------------------
-- Foreign Keys structure for table administration_adminsession
-- ----------------------------
ALTER TABLE "public"."administration_adminsession" ADD CONSTRAINT "administration_adminsession_user_id_241fef87_fk_auth_user_id" FOREIGN KEY ("user_id") REFERENCES "public"."auth_user" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION DEFERRABLE INITIALLY DEFERRED;

-- ----------------------------
-- Foreign Keys structure for table administration_adminuserprofile
-- ----------------------------
ALTER TABLE "public"."administration_adminuserprofile" ADD CONSTRAINT "administration_admin_user_id_41d9c186_fk_auth_user" FOREIGN KEY ("user_id") REFERENCES "public"."auth_user" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION DEFERRABLE INITIALLY DEFERRED;

-- ----------------------------
-- Foreign Keys structure for table administration_agentverification
-- ----------------------------
ALTER TABLE "public"."administration_agentverification" ADD CONSTRAINT "administration_agent_user_id_b243a0f0_fk_auth_user" FOREIGN KEY ("user_id") REFERENCES "public"."auth_user" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION DEFERRABLE INITIALLY DEFERRED;

-- ----------------------------
-- Foreign Keys structure for table administration_configurationsysteme
-- ----------------------------
ALTER TABLE "public"."administration_configurationsysteme" ADD CONSTRAINT "administration_confi_modifie_par_id_88650061_fk_auth_user" FOREIGN KEY ("modifie_par_id") REFERENCES "public"."auth_user" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION DEFERRABLE INITIALLY DEFERRED;

-- ----------------------------
-- Foreign Keys structure for table administration_dataversion
-- ----------------------------
ALTER TABLE "public"."administration_dataversion" ADD CONSTRAINT "administration_datav_changed_by_id_6a46c949_fk_auth_user" FOREIGN KEY ("changed_by_id") REFERENCES "public"."auth_user" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE "public"."administration_dataversion" ADD CONSTRAINT "administration_datav_content_type_id_4f1d180b_fk_django_co" FOREIGN KEY ("content_type_id") REFERENCES "public"."django_content_type" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION DEFERRABLE INITIALLY DEFERRED;

-- ----------------------------
-- Foreign Keys structure for table administration_permissiongroup
-- ----------------------------
ALTER TABLE "public"."administration_permissiongroup" ADD CONSTRAINT "administration_permi_created_by_id_7db6c623_fk_auth_user" FOREIGN KEY ("created_by_id") REFERENCES "public"."auth_user" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION DEFERRABLE INITIALLY DEFERRED;

-- ----------------------------
-- Foreign Keys structure for table administration_permissiongroup_users
-- ----------------------------
ALTER TABLE "public"."administration_permissiongroup_users" ADD CONSTRAINT "administration_permi_permissiongroup_id_42e3f701_fk_administr" FOREIGN KEY ("permissiongroup_id") REFERENCES "public"."administration_permissiongroup" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE "public"."administration_permissiongroup_users" ADD CONSTRAINT "administration_permi_user_id_cccfd414_fk_auth_user" FOREIGN KEY ("user_id") REFERENCES "public"."auth_user" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION DEFERRABLE INITIALLY DEFERRED;

-- ----------------------------
-- Foreign Keys structure for table administration_verificationqr
-- ----------------------------
ALTER TABLE "public"."administration_verificationqr" ADD CONSTRAINT "administration_verif_agent_id_fe3e4c9c_fk_administr" FOREIGN KEY ("agent_id") REFERENCES "public"."administration_agentverification" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE "public"."administration_verificationqr" ADD CONSTRAINT "administration_verif_qr_code_id_056a7eee_fk_payments_" FOREIGN KEY ("qr_code_id") REFERENCES "public"."payments_qrcode" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION DEFERRABLE INITIALLY DEFERRED;

-- ----------------------------
-- Foreign Keys structure for table auth_group_permissions
-- ----------------------------
ALTER TABLE "public"."auth_group_permissions" ADD CONSTRAINT "auth_group_permissio_permission_id_84c5c92e_fk_auth_perm" FOREIGN KEY ("permission_id") REFERENCES "public"."auth_permission" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE "public"."auth_group_permissions" ADD CONSTRAINT "auth_group_permissions_group_id_b120cbf9_fk_auth_group_id" FOREIGN KEY ("group_id") REFERENCES "public"."auth_group" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION DEFERRABLE INITIALLY DEFERRED;

-- ----------------------------
-- Foreign Keys structure for table auth_permission
-- ----------------------------
ALTER TABLE "public"."auth_permission" ADD CONSTRAINT "auth_permission_content_type_id_2f476e4b_fk_django_co" FOREIGN KEY ("content_type_id") REFERENCES "public"."django_content_type" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION DEFERRABLE INITIALLY DEFERRED;

-- ----------------------------
-- Foreign Keys structure for table auth_user_groups
-- ----------------------------
ALTER TABLE "public"."auth_user_groups" ADD CONSTRAINT "auth_user_groups_group_id_97559544_fk_auth_group_id" FOREIGN KEY ("group_id") REFERENCES "public"."auth_group" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE "public"."auth_user_groups" ADD CONSTRAINT "auth_user_groups_user_id_6a12ed8b_fk_auth_user_id" FOREIGN KEY ("user_id") REFERENCES "public"."auth_user" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION DEFERRABLE INITIALLY DEFERRED;

-- ----------------------------
-- Foreign Keys structure for table auth_user_user_permissions
-- ----------------------------
ALTER TABLE "public"."auth_user_user_permissions" ADD CONSTRAINT "auth_user_user_permi_permission_id_1fbb5f2c_fk_auth_perm" FOREIGN KEY ("permission_id") REFERENCES "public"."auth_permission" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE "public"."auth_user_user_permissions" ADD CONSTRAINT "auth_user_user_permissions_user_id_a95ead1b_fk_auth_user_id" FOREIGN KEY ("user_id") REFERENCES "public"."auth_user" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION DEFERRABLE INITIALLY DEFERRED;

-- ----------------------------
-- Foreign Keys structure for table core_auditlog
-- ----------------------------
ALTER TABLE "public"."core_auditlog" ADD CONSTRAINT "core_auditlog_user_id_3797aaab_fk_auth_user_id" FOREIGN KEY ("user_id") REFERENCES "public"."auth_user" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION DEFERRABLE INITIALLY DEFERRED;

-- ----------------------------
-- Foreign Keys structure for table core_companyprofile
-- ----------------------------
ALTER TABLE "public"."core_companyprofile" ADD CONSTRAINT "core_companyprofile_user_profile_id_2683e651_fk_core_user" FOREIGN KEY ("user_profile_id") REFERENCES "public"."core_userprofile" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION DEFERRABLE INITIALLY DEFERRED;

-- ----------------------------
-- Foreign Keys structure for table core_emergencyserviceprofile
-- ----------------------------
ALTER TABLE "public"."core_emergencyserviceprofile" ADD CONSTRAINT "core_emergencyservic_user_profile_id_f9008d1d_fk_core_user" FOREIGN KEY ("user_profile_id") REFERENCES "public"."core_userprofile" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION DEFERRABLE INITIALLY DEFERRED;

-- ----------------------------
-- Foreign Keys structure for table core_entrepriseprofile
-- ----------------------------
ALTER TABLE "public"."core_entrepriseprofile" ADD CONSTRAINT "core_entrepriseprofile_user_id_0dc94fc4_fk_auth_user_id" FOREIGN KEY ("user_id") REFERENCES "public"."auth_user" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION DEFERRABLE INITIALLY DEFERRED;

-- ----------------------------
-- Foreign Keys structure for table core_governmentadminprofile
-- ----------------------------
ALTER TABLE "public"."core_governmentadminprofile" ADD CONSTRAINT "core_governmentadmin_user_profile_id_3f6271bb_fk_core_user" FOREIGN KEY ("user_profile_id") REFERENCES "public"."core_userprofile" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION DEFERRABLE INITIALLY DEFERRED;

-- ----------------------------
-- Foreign Keys structure for table core_individualprofile
-- ----------------------------
ALTER TABLE "public"."core_individualprofile" ADD CONSTRAINT "core_individualprofi_user_profile_id_cf14067d_fk_core_user" FOREIGN KEY ("user_profile_id") REFERENCES "public"."core_userprofile" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION DEFERRABLE INITIALLY DEFERRED;

-- ----------------------------
-- Foreign Keys structure for table core_lawenforcementprofile
-- ----------------------------
ALTER TABLE "public"."core_lawenforcementprofile" ADD CONSTRAINT "core_lawenforcementp_user_profile_id_6c51382f_fk_core_user" FOREIGN KEY ("user_profile_id") REFERENCES "public"."core_userprofile" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION DEFERRABLE INITIALLY DEFERRED;

-- ----------------------------
-- Foreign Keys structure for table core_userprofile
-- ----------------------------
ALTER TABLE "public"."core_userprofile" ADD CONSTRAINT "core_userprofile_user_id_5141ad90_fk_auth_user_id" FOREIGN KEY ("user_id") REFERENCES "public"."auth_user" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION DEFERRABLE INITIALLY DEFERRED;

-- ----------------------------
-- Foreign Keys structure for table core_verificationdocument
-- ----------------------------
ALTER TABLE "public"."core_verificationdocument" ADD CONSTRAINT "core_verificationdoc_user_profile_id_e5c0fbfe_fk_core_user" FOREIGN KEY ("user_profile_id") REFERENCES "public"."core_userprofile" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE "public"."core_verificationdocument" ADD CONSTRAINT "core_verificationdoc_verified_by_id_b278dd82_fk_auth_user" FOREIGN KEY ("verified_by_id") REFERENCES "public"."auth_user" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION DEFERRABLE INITIALLY DEFERRED;

-- ----------------------------
-- Foreign Keys structure for table django_admin_log
-- ----------------------------
ALTER TABLE "public"."django_admin_log" ADD CONSTRAINT "django_admin_log_content_type_id_c4bce8eb_fk_django_co" FOREIGN KEY ("content_type_id") REFERENCES "public"."django_content_type" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE "public"."django_admin_log" ADD CONSTRAINT "django_admin_log_user_id_c564eba6_fk_auth_user_id" FOREIGN KEY ("user_id") REFERENCES "public"."auth_user" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION DEFERRABLE INITIALLY DEFERRED;

-- ----------------------------
-- Foreign Keys structure for table notifications_notification
-- ----------------------------
ALTER TABLE "public"."notifications_notification" ADD CONSTRAINT "notifications_notification_user_id_b5e8c0ff_fk_auth_user_id" FOREIGN KEY ("user_id") REFERENCES "public"."auth_user" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION DEFERRABLE INITIALLY DEFERRED;

-- ----------------------------
-- Foreign Keys structure for table payments_paiementtaxe
-- ----------------------------
ALTER TABLE "public"."payments_paiementtaxe" ADD CONSTRAINT "payments_paiementtax_vehicule_plaque_id_50717892_fk_vehicles_" FOREIGN KEY ("vehicule_plaque_id") REFERENCES "public"."vehicles_vehicule" ("plaque_immatriculation") ON DELETE NO ACTION ON UPDATE NO ACTION DEFERRABLE INITIALLY DEFERRED;

-- ----------------------------
-- Foreign Keys structure for table payments_qrcode
-- ----------------------------
ALTER TABLE "public"."payments_qrcode" ADD CONSTRAINT "payments_qrcode_vehicule_plaque_id_f9a46c70_fk_vehicles_" FOREIGN KEY ("vehicule_plaque_id") REFERENCES "public"."vehicles_vehicule" ("plaque_immatriculation") ON DELETE NO ACTION ON UPDATE NO ACTION DEFERRABLE INITIALLY DEFERRED;

-- ----------------------------
-- Foreign Keys structure for table socialaccount_socialaccount
-- ----------------------------
ALTER TABLE "public"."socialaccount_socialaccount" ADD CONSTRAINT "socialaccount_socialaccount_user_id_8146e70c_fk_auth_user_id" FOREIGN KEY ("user_id") REFERENCES "public"."auth_user" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION DEFERRABLE INITIALLY DEFERRED;

-- ----------------------------
-- Foreign Keys structure for table socialaccount_socialapp_sites
-- ----------------------------
ALTER TABLE "public"."socialaccount_socialapp_sites" ADD CONSTRAINT "socialaccount_social_site_id_2579dee5_fk_django_si" FOREIGN KEY ("site_id") REFERENCES "public"."django_site" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE "public"."socialaccount_socialapp_sites" ADD CONSTRAINT "socialaccount_social_socialapp_id_97fb6e7d_fk_socialacc" FOREIGN KEY ("socialapp_id") REFERENCES "public"."socialaccount_socialapp" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION DEFERRABLE INITIALLY DEFERRED;

-- ----------------------------
-- Foreign Keys structure for table socialaccount_socialtoken
-- ----------------------------
ALTER TABLE "public"."socialaccount_socialtoken" ADD CONSTRAINT "socialaccount_social_account_id_951f210e_fk_socialacc" FOREIGN KEY ("account_id") REFERENCES "public"."socialaccount_socialaccount" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE "public"."socialaccount_socialtoken" ADD CONSTRAINT "socialaccount_social_app_id_636a42d7_fk_socialacc" FOREIGN KEY ("app_id") REFERENCES "public"."socialaccount_socialapp" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION DEFERRABLE INITIALLY DEFERRED;

-- ----------------------------
-- Foreign Keys structure for table vehicles_documentvehicule
-- ----------------------------
ALTER TABLE "public"."vehicles_documentvehicule" ADD CONSTRAINT "vehicles_documentveh_uploaded_by_id_5f48f22c_fk_auth_user" FOREIGN KEY ("uploaded_by_id") REFERENCES "public"."auth_user" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE "public"."vehicles_documentvehicule" ADD CONSTRAINT "vehicles_documentveh_vehicule_id_f06206b9_fk_vehicles_" FOREIGN KEY ("vehicule_id") REFERENCES "public"."vehicles_vehicule" ("plaque_immatriculation") ON DELETE NO ACTION ON UPDATE NO ACTION DEFERRABLE INITIALLY DEFERRED;

-- ----------------------------
-- Foreign Keys structure for table vehicles_vehicule
-- ----------------------------
ALTER TABLE "public"."vehicles_vehicule" ADD CONSTRAINT "vehicles_vehicule_proprietaire_id_71bf2b83_fk_auth_user_id" FOREIGN KEY ("proprietaire_id") REFERENCES "public"."auth_user" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE "public"."vehicles_vehicule" ADD CONSTRAINT "vehicles_vehicule_type_vehicule_id_c51f9ee7_fk_vehicles_" FOREIGN KEY ("type_vehicule_id") REFERENCES "public"."vehicles_vehicletype" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION DEFERRABLE INITIALLY DEFERRED;
