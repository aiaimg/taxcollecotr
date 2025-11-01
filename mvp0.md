
---

## **Product Requirements Document (PRD): Digital Vehicle Tax Platform**

**Version:** 1.0
**Date:** October 26, 2023
**Author:** [Your Name/Team]
**Status:** Draft

### 1. Introduction & Executive Summary

This document outlines the requirements for a dedicated digital platform for the declaration and payment of the annual motor vehicle tax in Madagascar. This project is mandated by the provisions outlined in the "Projet de Loi de Finances 2026" (PLF 2026).

The platform will serve as the primary interface for vehicle owners to comply with the new tax law. It will automate tax calculation based on vehicle specifications, provide secure online payment options, and issue a verifiable digital and physical proof of payment in the form of a QR code. The goal is to create a modern, efficient, and user-friendly system that simplifies tax compliance for citizens and improves revenue collection for the government.

**Technical Stack:**
*   **Backend:** Django (Latest Version)
*   **Database:** PostgreSQL

### 2. Goals and Objectives

**Business Goals:**
*   **Modernize Tax Collection:** Replace manual processes with a streamlined, digital-first solution.
*   **Increase Compliance:** Make it easy and accessible for vehicle owners to pay their tax, reducing evasion.
*   **Improve Revenue Stream:** Ensure timely and accurate collection of vehicle taxes.
*   **Reduce Administrative Overhead:** Automate calculations, payment tracking, and receipt generation.
*   **Enable Effective Enforcement:** Provide law enforcement with a simple way to verify a vehicle's tax status.

**Product Goals:**
*   **User-Centric Design:** An intuitive and simple-to-use platform for all citizens, regardless of technical skill.
*   **Accuracy:** Ensure 100% accuracy in tax calculation according to the official legal grid.
*   **Security:** Protect user data and financial transactions with industry-best practices.
*   **Reliability:** Maintain high availability, especially during peak periods (e.g., leading up to the January 31st deadline).
*   **Accessibility:** The platform should be accessible on both desktop and mobile devices.

### 3. User Personas

1.  **Vehicle Owner (Individual Citizen):**
    *   **Description:** Owns one or two personal vehicles (car, motorcycle).
    *   **Goals:** Quickly find out how much they owe, pay easily, and get their proof of payment without visiting a government office.
    *   **Pain Points:** Forgetting the deadline, complex calculations, long queues at tax offices.

2.  **Fleet Manager (Business User):**
    *   **Description:** Manages a fleet of vehicles for a company (e.g., delivery vans, company cars).
    *   **Goals:** Manage all company vehicles in one place, perform bulk declarations and payments, and easily retrieve receipts for accounting.
    *   **Pain Points:** Manually processing taxes for dozens of vehicles is time-consuming and error-prone.

3.  **Government Administrator (Admin User):**
    *   **Description:** An employee of the tax authority.
    *   **Goals:** Monitor the system's performance, view reports on revenue collection, manage exceptions, look up vehicle/payment statuses, and update tax rates if the law changes in the future.
    *   **Pain Points:** Lack of real-time data on tax collection, difficulty tracking non-compliance.

4.  **Law Enforcement Officer (Indirect User):**
    *   **Description:** A police officer or gendarme on the road.
    *   **Goals:** To instantly and reliably verify if a vehicle's tax for the current year has been paid by scanning the QR code on the windshield.
    *   **Pain Points:** Inability to easily verify paper receipts, which can be forged.

### 4. Features & Requirements (User Stories)

#### 4.1. Core Platform

*   **FP-01: User Authentication**
    *   **As a new user, I want to** register for an account using my email address or phone number and a password.
    *   **As a registered user, I want to** log in securely to my account.
    *   **As a user, I want to** be able to reset my password if I forget it.

*   **FP-02: Vehicle Management**
    *   **As a vehicle owner, I want to** add a vehicle to my profile by providing its details:
        *   License Plate (Plaque d'immatriculation)
        *   Fiscal Power (Puissance Fiscale in CV)
        *   Engine Displacement (Cylindrée in Cm3)
        *   Energy Source (Source d'énergie: Essence, Diesel, Electrique, Hybride)
        *   Date of First Circulation (Date de première mise en circulation)
        *   Vehicle Category (e.g., Personal, Commercial, Ambulance, Fire Service, Administrative)
    *   **As a vehicle owner, I want to** see a list of all my registered vehicles and their current tax status (e.g., "Unpaid," "Paid," "Exempt").
    *   **As a fleet manager, I want to** be able to add, view, and manage multiple vehicles under a single company account.

#### 4.2. Tax Calculation & Declaration

*   **FP-03: Automated Tax Calculation**
    *   **As a user, I want** the system to automatically calculate the exact tax amount in Ariary for my vehicle based on the official grid.
    *   **The system MUST** accurately implement the logic from the "Montant en Ariary" table, using Fiscal Power, Energy Source, and Vehicle Age as inputs.
    *   **The system MUST** calculate the vehicle's age as: `Current Tax Year - Year of First Circulation`. The age bracket is determined on the first day of the tax period (January 1st).

*   **FP-04: Exemption Handling**
    *   **The system MUST** automatically identify exempt vehicles based on their category (Ambulance, Fire Service, Administrative, International Conventions) and display the tax amount as 0 Ariary or "Exempt."

#### 4.3. Payment Process

*   **FP-05: Secure Online Payment**
    *   **As a user, I want to** pay the calculated tax amount through a secure online payment gateway.
    *   **The system SHOULD** support common local payment methods (e.g., Mobile Money - MVola, Orange Money, Airtel Money; Credit/Debit Cards).
    *   **As a fleet manager, I want to** select multiple vehicles and pay for them in a single, consolidated transaction.

#### 4.4. Proof of Payment

*   **FP-06: Receipt and QR Code Generation**
    *   **As a user, upon successful payment, I want to** immediately receive a confirmation on-screen and via email.
    *   **As a user, I want to** be able to download a digital receipt (PDF format) for my records.
    *   **As a user, I want to** download a QR code that can be printed and affixed to my vehicle's windshield. The digital version should also be available in my account to be saved on my phone.

*   **FP-07: QR Code Verification**
    *   **The QR code, when scanned, MUST** lead to a public, non-authenticated verification page.
    *   This verification page **MUST** display the following information to prevent forgery:
        *   License Plate
        *   Tax Year
        *   Payment Status: **"PAYÉ"** (PAID) or **"EXONÉRÉ"** (EXEMPT)
        *   Date of Payment
        *   Expiry Date (e.g., 31 December [Current Year])
    *   The link should be unique and secure to prevent tampering.

#### 4.5. Deadlines & Notifications

*   **FP-08: Deadline Management**
    *   **The system MUST** enforce the payment deadlines as per Article I-102 bis:
        *   By January 31st for vehicles in service on January 1st.
        *   Immediately for vehicles newly put into circulation during the year.
    *   **As a user, I want to** receive email or SMS reminders before the payment deadline.

#### 4.6. Admin Dashboard

*   **FP-09: System Administration**
    *   **As an admin, I want to** view a dashboard with key metrics: total revenue collected, number of vehicles paid vs. unpaid, etc.
    *   **As an admin, I want to** be able to search for any vehicle by license plate or owner to check its status.
    *   **As an admin, I want to** have a secure interface to manage the tax rate table for future years.
    *   **As an admin, I want to** be able to manually handle specific cases or disputes.

### 5. Non-Functional Requirements

*   **Performance:** The system must be responsive, with page load times under 3 seconds. The QR verification page must load almost instantly.
*   **Scalability:** The architecture should handle high traffic loads, especially in January.
*   **Security:**
    *   All communications must be over HTTPS.
    *   User passwords must be securely hashed.
    *   The application must be protected against common web vulnerabilities (OWASP Top 10).
    *   Payment integration must be PCI-DSS compliant.
*   **Data Integrity:** The database must ensure that payment records are immutable and accurately linked to the correct vehicle and year.

### 6. High-Level Data Models (for PostgreSQL)

```sql
-- User Model (Leverages Django's built-in User model)
-- Profile model can extend this for company/individual details

CREATE TABLE Vehicle (
    license_plate VARCHAR(15) PRIMARY KEY,
    owner_id INT REFERENCES auth_user(id),
    fiscal_power_cv INT NOT NULL,
    engine_size_cm3 INT,
    energy_source VARCHAR(20) CHECK (energy_source IN ('Essence', 'Diesel', 'Electrique', 'Hybride')),
    first_registration_date DATE NOT NULL,
    vehicle_category VARCHAR(50) DEFAULT 'Personal', -- e.g., 'Personal', 'Ambulance', 'Administrative'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE TaxRate (
    id SERIAL PRIMARY KEY,
    min_power_cv INT,
    max_power_cv INT,
    energy_source VARCHAR(20),
    min_vehicle_age_years INT,
    max_vehicle_age_years INT,
    tax_amount_ariary NUMERIC(10, 2) NOT NULL,
    effective_year INT NOT NULL
);

CREATE TABLE TaxPayment (
    id SERIAL PRIMARY KEY,
    vehicle_license_plate VARCHAR(15) REFERENCES Vehicle(license_plate),
    tax_year INT NOT NULL,
    amount_due_ariary NUMERIC(10, 2),
    amount_paid_ariary NUMERIC(10, 2),
    payment_date TIMESTAMP WITH TIME ZONE,
    status VARCHAR(20) CHECK (status IN ('UNPAID', 'PAID', 'EXEMPT', 'PENDING')),
    payment_gateway_txn_id VARCHAR(100),
    qr_code_token VARCHAR(255) UNIQUE, -- Unique token for the verification URL
    UNIQUE (vehicle_license_plate, tax_year)
);
```

### 7. Assumptions and Dependencies

*   **Payment Gateway:** A reliable, local payment gateway provider must be identified and integrated.
*   **National Vehicle Registry:** It is assumed that there is no initial API access to a central vehicle registry. Therefore, vehicle data will be user-entered. The license plate will be the primary unique identifier.
*   **SMS/Email Service:** A third-party service (e.g., Twilio, SendGrid) will be required for sending notifications.
*   **Hosting:** The application will be hosted on a cloud infrastructure (e.g., AWS, Azure, Heroku) to ensure scalability and reliability.

### 8. Success Metrics

*   **Adoption Rate:** Percentage of eligible vehicles whose tax is paid via the platform.
*   **On-time Payment Rate:** Percentage of payments made before the January 31st deadline.
*   **User Satisfaction:** Measured via an optional, simple feedback form (e.g., Net Promoter Score).
*   **Reduction in Support Tickets:** A low number of users needing help indicates an intuitive system.
*   **System Uptime:** Target of 99.9% availability.