DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_tables WHERE tablename = 'workload_request') THEN
        CREATE TABLE workload_request (
            id UUID PRIMARY KEY,
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
            workload_request_id UUID NOT NULL,
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
            id UUID PRIMARY KEY,
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
            id UUID PRIMARY KEY,
            name VARCHAR(255),
            namespace VARCHAR(255),
            demand_cpu FLOAT NOT NULL,
            demand_memory FLOAT NOT NULL,
            demand_slack_cpu FLOAT,
            demand_slack_memory FLOAT,
            is_elastic BOOLEAN NOT NULL,
            assigned_node_id UUID,
            workload_request_id UUID NOT NULL,
            status VARCHAR(50) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (assigned_node_id) REFERENCES node(id)
        );
    END IF;
    RAISE NOTICE 'Table pod created or already exists.';
END $$;

DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_tables WHERE tablename = 'tuning_parameters') THEN
        CREATE TABLE tuning_parameters (
             id SERIAL PRIMARY KEY,
             output_1 FLOAT,
             output_2 FLOAT,
             output_3 FLOAT,
             alpha FLOAT,
             beta FLOAT,
             gamma FLOAT,
             created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    END IF;
    RAISE NOTICE 'Table tuning_parameters created or already exists.';
END $$;

DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_tables WHERE tablename = 'pod_request_decision') THEN
        CREATE TABLE pod_request_decision (
            id UUID PRIMARY KEY,
            pod_id UUID NOT NULL,
            pod_name VARCHAR(255) NOT NULL,
            namespace VARCHAR(255) NOT NULL,
            node_id UUID NOT NULL,
            is_elastic BOOLEAN NOT NULL,
            queue_name VARCHAR(255) NOT NULL,
            demand_cpu FLOAT NOT NULL,
            demand_memory FLOAT NOT NULL,
            demand_slack_cpu FLOAT,
            demand_slack_memory FLOAT,
            is_decision_status BOOLEAN NOT NULL,
            pod_parent_id UUID NOT NULL,
            pod_parent_kind VARCHAR(100) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    END IF;
    RAISE NOTICE 'Table pod_request_decision created or already exists.';
END $$;