import streamlit as st
import psycopg2
import uuid  # To generate unique IDs

# Connect to PostgreSQL server
#try:
connection = psycopg2.connect(
        host="localhost",
        database="car_rent_RDBMS",
        user="postgres",
        password="sahil",
        port=5000
        port=5432
    )
cursor = connection.cursor()
    ##st.write("Connected to the database successfully.")
#except Exception as e:
   # st.error(f"Error connecting to the database: {e}")





def create_tables():
    #try:
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

        
        # Create Car_OWNER table
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

        # Create RENTAL  table
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
        # Create REQUEST  table
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
               payment_id VARCHAR(50),
               FOREIGN KEY (request_id) REFERENCES Request(request_id),
               FOREIGN KEY (driver_id) REFERENCES Driver(driver_id),
               FOREIGN KEY (car_number_plate) REFERENCES Car(car_number)
            )
        ''')
        # Create the driver_bookings view
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
        booking_cursor CURSOR FOR 
            SELECT status FROM Request WHERE request_id = p_request_id FOR UPDATE;
    BEGIN
        OPEN booking_cursor;
        FETCH booking_cursor INTO v_status;
        IF v_status = 'Pending' THEN
            UPDATE Request
            SET assigned_driver = p_driver_id,
                status = 'Accepted'
            WHERE request_id = p_request_id;
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

        # Function for booking chain (recursive query)
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

        # Function for driver performance summary (using RANK and ROLLUP)
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

        #Trigger to update driver availability
        cursor.execute('''
           CREATE OR REPLACE FUNCTION update_driver_availability()
    RETURNS TRIGGER AS $$
    BEGIN
        IF NEW.status = 'Accepted' THEN
            UPDATE Driver
            SET account_status = 'inactive'
            WHERE driver_id = NEW.assigned_driver;
        ELSIF NEW.status = 'Completed' THEN
            UPDATE Driver
            SET account_status = 'active'
            WHERE driver_id = NEW.assigned_driver;
        END IF;
        RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;

    DROP TRIGGER IF EXISTS trg_update_driver_availability ON Request;
    CREATE TRIGGER trg_update_driver_availability
    AFTER UPDATE OF status ON Request
    FOR EACH ROW
    EXECUTE FUNCTION update_driver_availability();
        ''')

    #Procedure: Driver Ranking
        cursor.execute('''
            CREATE OR REPLACE PROCEDURE get_driver_rankings(
            IN p_criteria VARCHAR,
            INOUT p_result refcursor
        )
        LANGUAGE plpgsql AS $$
        BEGIN
            IF p_criteria = 'bookings' then
                OPEN p_result FOR
                SELECT
                    d.driver_id,
                    d.first_name || ' ' || d.last_name AS
                    driver_name,
                    COUNT(rental.rental_id) as booking_count,
                    RANK() OVER (ORDER BY COUNT(rental.rental_id) DESC) AS rank
                FROM Driver d
                LEFT JOIN Rental rental ON d.driver_id=rental.driver_id
                GROUP BY d.driver_id, d.first_name, d.last_name
                ORDER BY rank;
            ELSIF p_criteria = 'money' then
                OPEN p_result for 
                SELECT 
                    d.driver_id,
                    d.first_name || ' ' || d.last_name AS driver_name,
                    COALESCE(SUM(rental.total_amount*0.3), 0)
                    AS earnings,
                    RANK() OVER (ORDER BY COALESCE(SUM(rental.total_amount*0.3), 0)
                    DESC) AS rank
                FROM Driver d
                LEFT JOIN Rental rental ON d.driver_id=rental.driver_id
                GROUP BY d.driver_id, d.first_name, d.last_name
                ORDER BY rank;
            ELSE 
                RAISE EXCEPTION 'Invalid criteria: %', p_criteria;
            END IF;
        END;
        $$
        ''')

    # Procedure: Car Rankings
        cursor.execute('''
            CREATE OR REPLACE PROCEDURE get_car_rankings(
            IN p_criteria VARCHAR,
            INOUT p_result refcursor
        )
        LANGUAGE plpgsql AS $$
        BEGIN
            IF p_criteria = 'bookings' then
                OPEN p_result FOR
                SELECT
                    c.car_id,
                    c.car_number,
                    c.model,
                    COUNT(rental.rental_id) as booking_count,
                    RANK() OVER (ORDER by COUNT(rental.rental_id)
                    DESC) AS rank
                FROM Car c
                LEFT JOIN Rental rental on 
                rental.car_number_plate=c.car_number
                GROUP BY c.car_id, c.car_number, c.model
                ORDER BY rank;
            ELSIF p_criteria = 'money' THEN
                OPEN p_result FOR
                SELECT
                    c.car_id,
                    c.car_number,
                    c.model,
                    COALESCE(SUM(rental.total_amount*0.6), 0) AS revenue,
                    RANK() OVER (ORDER by COALESCE(SUM(rental.total_amount*0.6), 0)
                    DESC) AS rank
                FROM Car c
                LEFT JOIN Rental rental on 
                rental.car_number_plate=c.car_number
                GROUP BY c.car_id, c.car_number, c.model
                ORDER BY rank;
            ELSE 
                RAISE EXCEPTION 'Invalid criteria: %', p_criteria;
            END IF;
        END;
        $$
    ''')
    # Procedure: Customer Rankings 
        cursor.execute('''
            CREATE OR REPLACE PROCEDURE get_customer_rankings(
            IN p_criteria VARCHAR,
            INOUT p_result refcursor
        )
        LANGUAGE plpgsql AS $$
        BEGIN
            IF p_criteria = 'bookings' THEN
                OPEN p_result FOR
                SELECT 
                    c.customer_id,
                    c.first_name || ' ' || c.last_name AS customer_name,
                    COUNT(rental.rental_id) AS booking_count,
                    RANK() OVER (ORDER BY COUNT(rental.rental_id) DESC) AS rank
                FROM Customer c
                LEFT JOIN Request r ON c.customer_id = r.customer_id
                LEFT JOIN Rental rental ON r.request_id = rental.request_id
                GROUP BY c.customer_id, c.first_name, c.last_name
                ORDER BY rank;
            ELSIF p_criteria = 'money' THEN
                OPEN p_result FOR
                SELECT 
                    c.customer_id,
                    c.first_name || ' ' || c.last_name AS customer_name,
                    COALESCE(SUM(rental.total_amount), 0) AS spent,
                    RANK() OVER (ORDER BY COALESCE(SUM(rental.total_amount), 0) DESC) AS rank
                FROM Customer c
                LEFT JOIN Request r ON c.customer_id = r.customer_id
                LEFT JOIN Rental rental ON r.request_id = rental.request_id
                GROUP BY c.customer_id, c.first_name, c.last_name
                ORDER BY rank;
            ELSE
                RAISE EXCEPTION 'Invalid criteria: %', p_criteria;
            END IF;
        END;
        $$;
    ''')


        # Commit the changes
        connection.commit()
        #st.write("Tables created successfully.")

    #except Exception as e:
        #st.error(f"An error occurred while creating tables: {e}")
        connection.rollback()

create_tables()




# Function to insert data into the Admin table
def insert_admin(username, password, email):
    #try:
        # Generate a random UUID for admin_id
        admin_id = str(uuid.uuid4())

#         # Insert query including admin_id
#         insert_query = """
#         INSERT INTO admin (admin_id, username, password, email) VALUES (%s, %s, %s, %s);
#         """
#         cursor.execute(insert_query, (admin_id, username, password, email))
#         connection.commit()  # Commit the transaction
#         st.success(f"Admin '{username}' added successfully with ID: {admin_id}")
#     except Exception as e:
#         st.error(f"An error occurred while inserting data: {e}")
#         connection.rollback()

# # Streamlit UI for user input
# st.title("Insert Admin Data with UUID")

# # Input fields
# admin_username = st.text_input("Username", placeholder="Enter admin username")
# admin_password = st.text_input("Password", placeholder="Enter password", type="password")
# admin_email = st.text_input("Email", placeholder="Enter admin email")

# # Insert data on button click
# if st.button("Insert Admin"):
#     if admin_username and admin_password and admin_email:
#         insert_admin(admin_username, admin_password, admin_email)
#     else:
#         st.warning("Please fill out all fields before inserting.")