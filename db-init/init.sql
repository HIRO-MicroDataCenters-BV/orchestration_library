DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_tables WHERE tablename = 'workload_request') THEN
        CREATE TABLE workload_request (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            namespace VARCHAR(255) NOT NULL,
            api_version VARCHAR(50) NOT NULL,
            kind VARCHAR(50) NOT NULL,
            current_scale INT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    END IF;
    RAISE NOTICE 'Table workload_request created or already exists.';
END $$;

DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_tables WHERE tablename = 'workload_request_decision') THEN
        CREATE TABLE workload_request_decision (
            id UUID PRIMARY KEY,
            workload_request_id INT NOT NULL,
            node_name VARCHAR(255) NOT NULL,
            queue_name VARCHAR(255) NOT NULL,
            status VARCHAR(50) DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (workload_request_id) REFERENCES workload_request(id)
        );
    END IF;
    RAISE NOTICE 'Table workload_request_decision created or already exists.';
END $$;

DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_tables WHERE tablename = 'node') THEN
        CREATE TABLE node (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            status VARCHAR(50) DEFAULT 'active',
            cpu_capacity FLOAT NOT NULL,
            memory_capacity FLOAT NOT NULL,
            current_cpu_assignment FLOAT,
            current_memory_assignment FLOAT,
            current_cpu_utilization FLOAT,
            current_memory_utilization FLOAT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    END IF;
    RAISE NOTICE 'Table node created or already exists.';
END $$;

DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_tables WHERE tablename = 'pod') THEN
        CREATE TABLE pod (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255),
            namespace VARCHAR(255),
            demand_cpu FLOAT NOT NULL,
            demand_memory FLOAT NOT NULL,
            demand_slack_cpu FLOAT,
            demand_slack_memory FLOAT,
            is_elastic BOOLEAN NOT NULL,
            assigned_node_id INT,
            workload_request_id INT NOT NULL,
            status VARCHAR(50) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (assigned_node_id) REFERENCES node(id)
        );
    END IF;
    RAISE NOTICE 'Table pod created or already exists.';
END $$;

-- Create configuration table to test parameter changes
CREATE TABLE IF NOT EXISTS configuration_table (
    id SERIAL PRIMARY KEY,
    param_key VARCHAR(100),
    param_value VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create a function to notify listeners on config inserts, with debug logging
CREATE OR REPLACE FUNCTION notify_new_config()
RETURNS trigger AS $$
BEGIN
    -- Debug log to confirm the trigger fired
    RAISE NOTICE 'Trigger fired for new config: % = %', NEW.param_key, NEW.param_value;

    -- Send async notification
    PERFORM pg_notify('new_config', row_to_json(NEW)::text);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Drop old trigger if exists to avoid conflicts
DROP TRIGGER IF EXISTS config_change_trigger ON configuration_table;

-- Create new trigger to call notify function on INSERT
CREATE TRIGGER config_change_trigger
AFTER INSERT ON configuration_table
FOR EACH ROW
EXECUTE FUNCTION notify_new_config();
