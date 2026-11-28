PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS registrations (
    registration_id INTEGER PRIMARY KEY,

    -- Identity
    first_name TEXT,
    middle_name TEXT,
    last_name TEXT,
    provider_type TEXT CHECK (
        provider_type IN ('individual', 'agency')
    ),
    business_name TEXT,
    professional_title TEXT,
    service_start_year INTEGER,
    profile_photo TEXT,
    business_logo TEXT,
    additional_info TEXT,

    -- Account and contact information
    account_email TEXT NOT NULL COLLATE NOCASE UNIQUE,
    email TEXT,
    phone TEXT,
    phone_is_cell INTEGER CHECK (phone_is_cell IN (0, 1)),
    accepts_sms INTEGER CHECK (accepts_sms IN (0, 1)),
    secondary_phone TEXT,
    website TEXT,
    preferred_contact_method TEXT,
    agency_phone TEXT,
    agency_email TEXT,
    agency_website TEXT,
    calendar_url TEXT,

    -- Contact privacy
    phone_visibility TEXT NOT NULL DEFAULT 'public'
        CHECK (phone_visibility IN ('public', 'verified', 'hidden')),
    secondary_phone_visibility TEXT NOT NULL DEFAULT 'public'
        CHECK (secondary_phone_visibility IN ('public', 'verified', 'hidden')),
    email_visibility TEXT NOT NULL DEFAULT 'public'
        CHECK (email_visibility IN ('public', 'verified', 'hidden')),
    website_visibility TEXT NOT NULL DEFAULT 'public'
        CHECK (website_visibility IN ('public', 'verified', 'hidden')),
    agency_phone_visibility TEXT NOT NULL DEFAULT 'public'
        CHECK (agency_phone_visibility IN ('public', 'verified', 'hidden')),
    agency_email_visibility TEXT NOT NULL DEFAULT 'public'
        CHECK (agency_email_visibility IN ('public', 'verified', 'hidden')),
    agency_website_visibility TEXT NOT NULL DEFAULT 'public'
        CHECK (agency_website_visibility IN ('public', 'verified', 'hidden')),
    calendar_visibility TEXT NOT NULL DEFAULT 'public'
        CHECK (calendar_visibility IN ('public', 'verified', 'hidden')),
    address_visibility TEXT NOT NULL DEFAULT 'hidden'
        CHECK (address_visibility IN ('public', 'verified', 'hidden')),

    -- Geographic coverage
    address TEXT,
    address_unit TEXT,
    city TEXT,
    state_code TEXT,
    county TEXT,
    zip_code TEXT,
    country_code TEXT NOT NULL DEFAULT 'US',
    reference_point TEXT,
    latitude REAL CHECK (latitude BETWEEN -90 AND 90),
    longitude REAL CHECK (longitude BETWEEN -180 AND 180),
    travel_radius_miles REAL CHECK (travel_radius_miles >= 0),
    service_counties TEXT,
    service_states TEXT,
    service_area TEXT,
    statewide_virtual_services INTEGER
        CHECK (statewide_virtual_services IN (0, 1)),

    -- Services
    supervised_visitation INTEGER
        CHECK (supervised_visitation IN (0, 1)),
    supervised_exchange INTEGER
        CHECK (supervised_exchange IN (0, 1)),
    transportation INTEGER CHECK (transportation IN (0, 1)),
    virtual_visitation INTEGER CHECK (virtual_visitation IN (0, 1)),
    on_site_visitation INTEGER CHECK (on_site_visitation IN (0, 1)),
    off_site_visitation INTEGER CHECK (off_site_visitation IN (0, 1)),
    in_home_visitation INTEGER CHECK (in_home_visitation IN (0, 1)),
    telephone_visitation INTEGER CHECK (telephone_visitation IN (0, 1)),
    overnight_visitation INTEGER CHECK (overnight_visitation IN (0, 1)),
    travel_supervision INTEGER CHECK (travel_supervision IN (0, 1)),
    therapeutic_visitation INTEGER CHECK (therapeutic_visitation IN (0, 1)),
    supportive_visitation INTEGER CHECK (supportive_visitation IN (0, 1)),
    court_testimony INTEGER CHECK (court_testimony IN (0, 1)),
    parent_education INTEGER CHECK (parent_education IN (0, 1)),
    parent_coaching INTEGER CHECK (parent_coaching IN (0, 1)),
    parenting_coordination INTEGER CHECK (parenting_coordination IN (0, 1)),
    reunification_support INTEGER CHECK (reunification_support IN (0, 1)),
    other_services TEXT,

    -- Reports
    handwritten_reports INTEGER CHECK (handwritten_reports IN (0, 1)),
    typed_reports INTEGER CHECK (typed_reports IN (0, 1)),
    reports_included INTEGER CHECK (reports_included IN (0, 1)),
    report_turnaround_days INTEGER CHECK (report_turnaround_days >= 0),

    -- Pricing policies
    sliding_scale INTEGER CHECK (sliding_scale IN (0, 1)),
    subsidized_services INTEGER CHECK (subsidized_services IN (0, 1)),
    charges_roundtrip_mileage INTEGER
        CHECK (charges_roundtrip_mileage IN (0, 1)),
    charges_roundtrip_driving_time INTEGER
        CHECK (charges_roundtrip_driving_time IN (0, 1)),
    billing_increment_minutes INTEGER CHECK (billing_increment_minutes > 0),
    pricing_notes TEXT,

    -- Payment methods
    accepts_cash INTEGER CHECK (accepts_cash IN (0, 1)),
    accepts_check INTEGER CHECK (accepts_check IN (0, 1)),
    accepts_credit_card INTEGER CHECK (accepts_credit_card IN (0, 1)),
    accepts_debit_card INTEGER CHECK (accepts_debit_card IN (0, 1)),
    accepts_zelle INTEGER CHECK (accepts_zelle IN (0, 1)),
    accepts_venmo INTEGER CHECK (accepts_venmo IN (0, 1)),
    accepts_paypal INTEGER CHECK (accepts_paypal IN (0, 1)),
    accepts_cash_app INTEGER CHECK (accepts_cash_app IN (0, 1)),
    advance_payment_required INTEGER
        CHECK (advance_payment_required IN (0, 1)),
    payment_plans INTEGER CHECK (payment_plans IN (0, 1)),
    payment_notes TEXT,

    -- Availability
    accepting_new_clients INTEGER CHECK (accepting_new_clients IN (0, 1)),
    available_monday INTEGER CHECK (available_monday IN (0, 1)),
    available_tuesday INTEGER CHECK (available_tuesday IN (0, 1)),
    available_wednesday INTEGER CHECK (available_wednesday IN (0, 1)),
    available_thursday INTEGER CHECK (available_thursday IN (0, 1)),
    available_friday INTEGER CHECK (available_friday IN (0, 1)),
    available_saturday INTEGER CHECK (available_saturday IN (0, 1)),
    available_sunday INTEGER CHECK (available_sunday IN (0, 1)),
    timezone TEXT,
    available_holidays INTEGER CHECK (available_holidays IN (0, 1)),
    flexible_scheduling INTEGER CHECK (flexible_scheduling IN (0, 1)),
    short_notice_available INTEGER CHECK (short_notice_available IN (0, 1)),
    next_available_date TEXT,
    advance_notice_hours REAL CHECK (advance_notice_hours >= 0),
    availability_notes TEXT,

    -- Visit conditions
    minimum_visit_minutes INTEGER CHECK (minimum_visit_minutes > 0),
    maximum_visit_minutes INTEGER CHECK (maximum_visit_minutes > 0),
    minimum_virtual_minutes INTEGER CHECK (minimum_virtual_minutes > 0),
    maximum_children INTEGER CHECK (maximum_children > 0),
    minimum_child_age INTEGER CHECK (minimum_child_age >= 0),
    maximum_child_age INTEGER CHECK (maximum_child_age >= 0),
    intake_required INTEGER CHECK (intake_required IN (0, 1)),
    court_order_required INTEGER CHECK (court_order_required IN (0, 1)),
    service_agreement_required INTEGER
        CHECK (service_agreement_required IN (0, 1)),
    cancellation_notice_hours REAL CHECK (cancellation_notice_hours >= 0),
    cancellation_policy TEXT,
    intake_notes TEXT,
    visit_restrictions TEXT,
    policy_notes TEXT,

    -- Languages and experience
    languages TEXT,
    interpreter_available INTEGER CHECK (interpreter_available IN (0, 1)),
    special_needs_experience INTEGER CHECK (special_needs_experience IN (0, 1)),
    autism_experience INTEGER CHECK (autism_experience IN (0, 1)),
    infant_experience INTEGER CHECK (infant_experience IN (0, 1)),
    toddler_experience INTEGER CHECK (toddler_experience IN (0, 1)),
    teenager_experience INTEGER CHECK (teenager_experience IN (0, 1)),
    domestic_violence_experience INTEGER
        CHECK (domestic_violence_experience IN (0, 1)),
    high_conflict_experience INTEGER CHECK (high_conflict_experience IN (0, 1)),
    substance_abuse_experience INTEGER
        CHECK (substance_abuse_experience IN (0, 1)),
    child_welfare_experience INTEGER CHECK (child_welfare_experience IN (0, 1)),
    foster_care_experience INTEGER CHECK (foster_care_experience IN (0, 1)),
    experience_notes TEXT,

    -- Training and qualifications
    training_organization TEXT,
    training_completed_at TEXT,
    training_hours REAL CHECK (training_hours >= 0),
    training_expires_at TEXT,
    svn_training_completed INTEGER CHECK (svn_training_completed IN (0, 1)),
    svn_management_training INTEGER CHECK (svn_management_training IN (0, 1)),
    exchange_training_completed INTEGER CHECK (exchange_training_completed IN (0, 1)),
    transportation_training_completed INTEGER
        CHECK (transportation_training_completed IN (0, 1)),
    additional_training TEXT,
    professional_credentials TEXT,
    license_type TEXT,
    license_state TEXT,
    license_number TEXT,
    license_expires_at TEXT,
    cpr_certified INTEGER CHECK (cpr_certified IN (0, 1)),
    first_aid_certified INTEGER CHECK (first_aid_certified IN (0, 1)),
    svn_member INTEGER CHECK (svn_member IN (0, 1)),
    memberships TEXT,
    court_listings TEXT,

    -- Background screening and insurance
    background_check_completed INTEGER
        CHECK (background_check_completed IN (0, 1)),
    background_check_date TEXT,
    fingerprint_screening INTEGER CHECK (fingerprint_screening IN (0, 1)),
    trustline_registered INTEGER CHECK (trustline_registered IN (0, 1)),
    liability_insurance INTEGER CHECK (liability_insurance IN (0, 1)),
    auto_insurance INTEGER CHECK (auto_insurance IN (0, 1)),
    bonded INTEGER CHECK (bonded IN (0, 1)),
    qualification_notes TEXT,

    -- Environment and facilities
    is_smoker INTEGER CHECK (is_smoker IN (0, 1)),
    uses_vape INTEGER CHECK (uses_vape IN (0, 1)),
    smoke_free_vehicle INTEGER CHECK (smoke_free_vehicle IN (0, 1)),
    smoke_free_facility INTEGER CHECK (smoke_free_facility IN (0, 1)),
    wheelchair_accessible INTEGER CHECK (wheelchair_accessible IN (0, 1)),
    safety_notes TEXT,

    -- Account verification and agreements
    email_verified_at TEXT,
    phone_verified_at TEXT,
    terms_accepted INTEGER NOT NULL DEFAULT 0
        CHECK (terms_accepted IN (0, 1)),
    terms_accepted_at TEXT,
    terms_version TEXT,
    privacy_acknowledged INTEGER NOT NULL DEFAULT 0
        CHECK (privacy_acknowledged IN (0, 1)),
    privacy_acknowledged_at TEXT,
    privacy_version TEXT,

    -- Registration lifecycle
    status TEXT NOT NULL DEFAULT 'hidden'
        CHECK (status IN ('active', 'hidden', 'deleted')),
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_login_at TEXT,
    last_published_at TEXT,
    deleted_at TEXT,

    CHECK (minimum_visit_minutes <= maximum_visit_minutes),
    CHECK (minimum_child_age <= maximum_child_age),
    CHECK ((latitude IS NULL) = (longitude IS NULL))
);


-- Monday = 0, Sunday = 6.
-- Multiple time ranges per day are supported.

CREATE TABLE IF NOT EXISTS registration_availability (
    availability_id INTEGER PRIMARY KEY,
    registration_id INTEGER NOT NULL
        REFERENCES registrations(registration_id) ON DELETE CASCADE,
    day_of_week INTEGER NOT NULL
        CHECK (day_of_week BETWEEN 0 AND 6),
    start_time TEXT NOT NULL
        CHECK (
            start_time GLOB '[0-2][0-9]:[0-5][0-9]'
            AND start_time < '24:00'
        ),
    end_time TEXT NOT NULL
        CHECK (
            end_time GLOB '[0-2][0-9]:[0-5][0-9]'
            AND end_time <= '24:00'
            AND (end_time < '24:00' OR end_time = '24:00')
        ),
    CHECK (start_time < end_time),
    UNIQUE (registration_id, day_of_week, start_time, end_time)
);


-- Amounts are stored in thousandths of a dollar.
-- Examples:
-- $100.00 = 100000
-- $0.76   = 760
-- $0.725  = 725
-- $0.00   = 0
-- No record means unspecified.

CREATE TABLE IF NOT EXISTS registration_rates (
    rate_id INTEGER PRIMARY KEY,
    registration_id INTEGER NOT NULL
        REFERENCES registrations(registration_id) ON DELETE CASCADE,

    rate_type TEXT NOT NULL CHECK (rate_type IN (
        'hourly_rate',
        'exchange_rate',
        'intake_fee',
        'price_per_mile',
        'driving_hourly_rate',
        'on_site_hourly_rate',
        'off_site_hourly_rate',
        'in_home_hourly_rate',
        'virtual_hourly_rate',
        'telephone_hourly_rate',
        'therapeutic_hourly_rate',
        'transportation_hourly_rate',
        'orientation_fee',
        'consultation_fee',
        'additional_child_fee',
        'report_fee',
        'court_appearance_fee',
        'overnight_fee',
        'cancellation_fee',
        'no_show_fee',
        'weekend_surcharge',
        'holiday_surcharge',
        'rush_service_fee'
    )),

    amount INTEGER NOT NULL
        CHECK (typeof(amount) = 'integer' AND amount >= 0),

    billing_unit TEXT NOT NULL CHECK (billing_unit IN (
        'hour',
        'mile',
        'visit',
        'exchange',
        'intake',
        'orientation',
        'consultation',
        'child',
        'report',
        'appearance',
        'night',
        'occurrence',
        'flat'
    )),

    minimum_children INTEGER CHECK (minimum_children > 0),
    maximum_children INTEGER CHECK (maximum_children > 0),
    rate_notes TEXT,

    CHECK (minimum_children <= maximum_children),

    CHECK (
        rate_type != 'price_per_mile'
        OR billing_unit = 'mile'
    ),

    CHECK (
        rate_type NOT LIKE '%hourly_rate'
        OR billing_unit = 'hour'
    )
);


CREATE INDEX IF NOT EXISTS idx_registrations_phone
    ON registrations(phone);

CREATE INDEX IF NOT EXISTS idx_registrations_email
    ON registrations(email COLLATE NOCASE);

CREATE INDEX IF NOT EXISTS idx_registrations_geography
    ON registrations(state_code, county, zip_code);

CREATE INDEX IF NOT EXISTS idx_registrations_status
    ON registrations(status);

CREATE INDEX IF NOT EXISTS idx_registration_rates_provider
    ON registration_rates(registration_id, rate_type);

CREATE INDEX IF NOT EXISTS idx_registration_rates_search
    ON registration_rates(rate_type, amount);
