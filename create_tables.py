import streamlit as st
import psycopg2
import uuid

# Connect to PostgreSQL server
connection = psycopg2.connect(
        host="localhost",
        database="car_rent_RDBMS",
        user="postgres",
        password="kyo29sue",
        port=5432
    )
cursor = connection.cursor()

def create_tables():
    try:
        # Enable uuid-ossp extension
        cursor.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp";')

        # Create Customer table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Customer (
                customer_id VARCHAR(50) PRIMARY KEY,
                first_name VARCHAR(100),
                last_name VARCHAR(100),
                email VARCHAR(100) UNIQUE,
                password VARCHAR(100),
                phone VARCHAR(20),
                address TEXT,
                account_status VARCHAR(20)
            )
        ''')

        # Create Driver table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Driver (
                driver_id VARCHAR(50) PRIMARY KEY,
                first_name VARCHAR(100),
                last_name VARCHAR(100),
                email VARCHAR(100) UNIQUE,
                password VARCHAR(100),
                phone VARCHAR(20),
                address TEXT,
                location VARCHAR(100),
                license_number VARCHAR(50),
                account_status VARCHAR(20)
            )
        ''')

        # Create Admin table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Admin (
                admin_id VARCHAR(50) PRIMARY KEY,
                username VARCHAR(100),
                email VARCHAR(100) UNIQUE,
                password VARCHAR(100)
            )
        ''')

        # Create Car_Owner table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Car_Owner (
                car_owner_id VARCHAR(50) PRIMARY KEY,
                first_name VARCHAR(100),
                last_name VARCHAR(100),
                email VARCHAR(100) UNIQUE,
                password VARCHAR(200),
                phone VARCHAR(20),
                address TEXT,
                location VARCHAR(100),
                account_status VARCHAR(20)
            )
        ''')

        # Create Car table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Car (
                car_id SERIAL PRIMARY KEY,
                car_number VARCHAR(50) UNIQUE,
                model VARCHAR(100),
                seats INT,
                car_owner_id VARCHAR(100),
                availability_status VARCHAR(20),
                car_type VARCHAR(50),
                FOREIGN KEY (car_owner_id) REFERENCES Car_Owner(car_owner_id)
            )
        ''')

        # Create Request table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Request (
                request_id VARCHAR(50) PRIMARY KEY,
                customer_id VARCHAR(50),
                car_type VARCHAR(50),
                pickup_date TIMESTAMP,
                dropoff_date TIMESTAMP,
                pickup_location VARCHAR(100),
                dropoff_location VARCHAR(100),
                duration NUMERIC,
                payment_status VARCHAR(20),
                assigned_driver VARCHAR(50),
                car_number_plate VARCHAR(20),
                status VARCHAR(20),
                FOREIGN KEY (customer_id) REFERENCES Customer(customer_id),
                FOREIGN KEY (assigned_driver) REFERENCES Driver(driver_id),
                FOREIGN KEY (car_number_plate) REFERENCES Car(car_number)
            )
        ''')

        # Create Rental table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Rental (
                rental_id VARCHAR(50) PRIMARY KEY,
                request_id VARCHAR(50),
                driver_id VARCHAR(50),
                car_number_plate VARCHAR(20),
                pickup_date TIMESTAMP,
                dropoff_date TIMESTAMP,
                status VARCHAR(20),
                total_amount NUMERIC,
                owner_share NUMERIC,
                payment_id VARCHAR(50),
                FOREIGN KEY (request_id) REFERENCES Request(request_id),
                FOREIGN KEY (driver_id) REFERENCES Driver(driver_id),
                FOREIGN KEY (car_number_plate) REFERENCES Car(car_number)
            )
        ''')

        # Add owner_share column if it doesn't exist
        cursor.execute('''
            DO $$
            BEGIN
                IF NOT EXISTS (
                    SELECT 1 
                    FROM information_schema.columns 
                    WHERE table_name = 'rental' 
                    AND column_name = 'owner_share'
                ) THEN
                    ALTER TABLE Rental ADD COLUMN owner_share NUMERIC;
                END IF;
            END $$;
        ''')

        # Create driver_bookings view
        cursor.execute('''
            CREATE OR REPLACE VIEW driver_bookings AS
            SELECT 
                d.driver_id,
                d.first_name || ' ' || d.last_name AS driver_name,
                r.request_id,
                r.car_type,
                r.pickup_date,
                r.dropoff_date,
                r.status
            FROM Driver d
            LEFT JOIN Request r ON d.driver_id = r.assigned_driver
            WHERE r.status IS NOT NULL;
        ''')

        # Procedure to assign bookings
        cursor.execute('''
            CREATE OR REPLACE PROCEDURE assign_driver_booking(
                p_driver_id VARCHAR,
                p_request_id VARCHAR
            )
            LANGUAGE plpgsql AS $$
            DECLARE
                v_status VARCHAR;
                v_car_number VARCHAR;
                booking_cursor CURSOR FOR 
                    SELECT status, car_number_plate FROM Request WHERE request_id = p_request_id FOR UPDATE;
            BEGIN
                OPEN booking_cursor;
                FETCH booking_cursor INTO v_status, v_car_number;
                IF v_status = 'Pending' THEN
                    UPDATE Request
                    SET assigned_driver = p_driver_id,
                        status = 'Accepted'
                    WHERE request_id = p_request_id;
                    IF v_car_number IS NOT NULL THEN
                        CALL update_car_availability(v_car_number, 'Not Available');
                    END IF;
                    RAISE NOTICE 'Booking % assigned to driver %', p_request_id, p_driver_id;
                ELSE
                    RAISE EXCEPTION 'Booking % is not available for assignment', p_request_id;
                END IF;
                CLOSE booking_cursor;
            END;
            $$;
        ''')

        # Function to calculate driver earnings
        cursor.execute('''
            CREATE OR REPLACE FUNCTION calculate_driver_earnings(p_driver_id VARCHAR)
            RETURNS NUMERIC AS $$
            DECLARE
                v_total_earnings NUMERIC := 0;
                v_duration NUMERIC;
                v_car_type VARCHAR;
            BEGIN
                FOR v_duration, v_car_type IN 
                    SELECT duration, car_type 
                    FROM Request 
                    WHERE assigned_driver = p_driver_id AND status = 'Completed'
                LOOP
                    v_total_earnings := v_total_earnings + 
                        CASE UPPER(v_car_type)
                            WHEN 'PREMIO' THEN v_duration * 20
                            WHEN 'COROLLA' THEN v_duration * 15
                            WHEN 'X COROLLA' THEN v_duration * 18
                            WHEN 'NOAH' THEN v_duration * 25
                            WHEN 'WAGON' THEN v_duration * 22
                            WHEN 'TRUCK' THEN v_duration * 30
                            ELSE v_duration * 10
                        END;
                END LOOP;
                RETURN ROUND(v_total_earnings, 2);
            END;
            $$ LANGUAGE plpgsql;
        ''')

        # Function for booking chain
        cursor.execute('''
            CREATE OR REPLACE FUNCTION get_booking_chain(p_driver_id VARCHAR)
            RETURNS TABLE (
                request_id VARCHAR,
                pickup_date TIMESTAMP,
                dropoff_date TIMESTAMP
            ) AS $$
            BEGIN
                RETURN QUERY
                WITH RECURSIVE booking_chain AS (
                    SELECT r.request_id, r.pickup_date, r.dropoff_date
                    FROM Request r
                    WHERE r.assigned_driver = p_driver_id AND r.status = 'Accepted'
                    UNION ALL
                    SELECT r.request_id, r.pickup_date, r.dropoff_date
                    FROM Request r
                    INNER JOIN booking_chain bc ON r.assigned_driver = p_driver_id
                    WHERE r.pickup_date > bc.dropoff_date AND r.status = 'Accepted'
                )
                SELECT * FROM booking_chain ORDER BY pickup_date;
            END;
            $$ LANGUAGE plpgsql;
        ''')

        # Function for driver performance summary
        cursor.execute('''
            DROP FUNCTION IF EXISTS driver_performance_summary(VARCHAR);
            CREATE OR REPLACE FUNCTION driver_performance_summary(p_driver_id VARCHAR)
            RETURNS TABLE (
                metric TEXT,
                value NUMERIC
            ) AS $$
            BEGIN
                RETURN QUERY
                WITH stats AS (
                    SELECT 
                        assigned_driver,
                        COUNT(*) AS total_bookings,
                        SUM(duration) AS total_hours,
                        RANK() OVER (ORDER BY COUNT(*) DESC) AS booking_rank
                    FROM Request
                    WHERE assigned_driver = p_driver_id AND status = 'Completed'
                    GROUP BY ROLLUP(assigned_driver)
                )
                SELECT 'Total Bookings', total_bookings::NUMERIC FROM stats WHERE assigned_driver IS NOT NULL
                UNION ALL
                SELECT 'Total Hours', total_hours::NUMERIC FROM stats WHERE assigned_driver IS NOT NULL
                UNION ALL
                SELECT 'Booking Rank', booking_rank::NUMERIC FROM stats WHERE assigned_driver IS NOT NULL
                UNION ALL
                SELECT 'Overall Bookings', total_bookings::NUMERIC FROM stats WHERE assigned_driver IS NULL;
            END;
            $$ LANGUAGE plpgsql;
        ''')

        # Trigger to update driver and car availability
        cursor.execute('''
            CREATE OR REPLACE FUNCTION update_driver_and_car_availability()
            RETURNS TRIGGER AS $$
            BEGIN
                IF NEW.status = 'Accepted' THEN
                    UPDATE Driver
                    SET account_status = 'inactive'
                    WHERE driver_id = NEW.assigned_driver;
                    IF NEW.car_number_plate IS NOT NULL THEN
                        UPDATE Car
                        SET availability_status = 'Not Available'
                        WHERE car_number = NEW.car_number_plate;
                    END IF;
                ELSIF NEW.status = 'Completed' THEN
                    UPDATE Driver
                    SET account_status = 'active'
                    WHERE driver_id = NEW.assigned_driver;
                    IF NEW.car_number_plate IS NOT NULL THEN
                        UPDATE Car
                        SET availability_status = 'Available'
                        WHERE car_number = NEW.car_number_plate;
                    END IF;
                END IF;
                RETURN NEW;
            END;
            $$ LANGUAGE plpgsql;

            DROP TRIGGER IF EXISTS trg_update_driver_and_car_availability ON Request;
            CREATE TRIGGER trg_update_driver_and_car_availability
            AFTER UPDATE OF status ON Request
            FOR EACH ROW
            EXECUTE FUNCTION update_driver_and_car_availability();
        ''')

        # Function to calculate owner earnings
        cursor.execute('''
            CREATE OR REPLACE FUNCTION calculate_owner_earnings(p_car_owner_id VARCHAR)
            RETURNS NUMERIC AS $$
            DECLARE
                v_total_earnings NUMERIC := 0;
            BEGIN
                SELECT COALESCE(SUM(owner_share), 0)
                INTO v_total_earnings
                FROM Rental r
                JOIN Car c ON r.car_number_plate = c.car_number
                WHERE c.car_owner_id = p_car_owner_id AND r.status = 'Completed';
                RETURN ROUND(v_total_earnings, 2);
            END;
            $$ LANGUAGE plpgsql;
        ''')

        # Function for car performance summary
        cursor.execute('''
            CREATE OR REPLACE FUNCTION car_performance_summary(p_car_owner_id VARCHAR)
            RETURNS TABLE (
                metric TEXT,
                value NUMERIC
            ) AS $$
            BEGIN
                RETURN QUERY
                WITH stats AS (
                    SELECT 
                        c.car_owner_id,
                        COUNT(r.request_id) AS total_bookings,
                        SUM(r.duration) AS total_hours,
                        RANK() OVER (ORDER BY COUNT(r.request_id) DESC) AS booking_rank
                    FROM Car c
                    LEFT JOIN Request r ON c.car_number = r.car_number_plate
                    WHERE c.car_owner_id = p_car_owner_id AND r.status = 'Completed'
                    GROUP BY ROLLUP(c.car_owner_id)
                )
                SELECT 'Total Bookings', total_bookings::NUMERIC FROM stats WHERE car_owner_id IS NOT NULL
                UNION ALL
                SELECT 'Total Hours', total_hours::NUMERIC FROM stats WHERE car_owner_id IS NOT NULL
                UNION ALL
                SELECT 'Booking Rank', booking_rank::NUMERIC FROM stats WHERE car_owner_id IS NOT NULL
                UNION ALL
                SELECT 'Overall Bookings', total_bookings::NUMERIC FROM stats WHERE car_owner_id IS NULL;
            END;
            $$ LANGUAGE plpgsql;
        ''')

        # Procedure to update car availability
        cursor.execute('''
            CREATE OR REPLACE PROCEDURE update_car_availability(
                p_car_number VARCHAR,
                p_status VARCHAR
            )
            LANGUAGE plpgsql AS $$
            BEGIN
                UPDATE Car
                SET availability_status = p_status
                WHERE car_number = p_car_number;
                RAISE NOTICE 'Car % availability updated to %', p_car_number, p_status;
            END;
            $$;
        ''')

        # Procedure to finalize booking and calculate revenue
        cursor.execute('''
            CREATE OR REPLACE PROCEDURE finalize_booking(
                p_request_id VARCHAR,
                p_driver_id VARCHAR,
                p_car_number VARCHAR
            )
            LANGUAGE plpgsql AS $$
            DECLARE
                v_duration NUMERIC;
                v_car_type VARCHAR;
                v_total_amount NUMERIC;
                v_owner_share NUMERIC;
                v_rental_id VARCHAR := uuid_generate_v4()::VARCHAR;
            BEGIN
                SELECT duration, car_type
                INTO v_duration, v_car_type
                FROM Request
                WHERE request_id = p_request_id;

                v_total_amount := CASE UPPER(v_car_type)
                    WHEN 'PREMIO' THEN v_duration * 50
                    WHEN 'COROLLA' THEN v_duration * 40
                    WHEN 'X COROLLA' THEN v_duration * 45
                    WHEN 'NOAH' THEN v_duration * 60
                    WHEN 'WAGON' THEN v_duration * 55
                    WHEN 'TRUCK' THEN v_duration * 70
                    ELSE v_duration * 30
                END;
                v_owner_share := v_total_amount * 0.7;

                INSERT INTO Rental (
                    rental_id, request_id, driver_id, car_number_plate,
                    pickup_date, dropoff_date, status, total_amount, owner_share, payment_id
                )
                SELECT
                    v_rental_id, p_request_id, p_driver_id, p_car_number,
                    pickup_date, dropoff_date, 'Completed', v_total_amount, v_owner_share, NULL
                FROM Request
                WHERE request_id = p_request_id;

                RAISE NOTICE 'Booking % finalized: Total $%, Owner Share $%', p_request_id, v_total_amount, v_owner_share;
            END;
            $$;
        ''')

        # Commit the changes
        connection.commit()
        # st.write("Tables and objects created successfully.")

    except Exception as e:
        connection.rollback()
        # st.error(f"An error occurred while creating tables: {e}")

create_tables()

def insert_admin(username, password, email):
    try:
        admin_id = str(uuid.uuid4())
        insert_query = """
        INSERT INTO admin (admin_id, username, password, email) VALUES (%s, %s, %s, %s);
        """
        cursor.execute(insert_query, (admin_id, username, password, email))
        connection.commit()
    except Exception as e:
        connection.rollback()
