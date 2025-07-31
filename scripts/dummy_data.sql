-- Delete only the dummy data rows before inserting

DELETE FROM workload_request_decision
WHERE id IN (
    'eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeee',
    'ffffffff-ffff-ffff-ffff-ffffffffffff',
    '99999999-9999-9999-9999-999999999999',
    '88888888-8888-8888-8888-888888888888',
    '33333333-4444-5555-6666-777777777777',
    '44444444-5555-6666-7777-888888888888',
    '55555555-6666-7777-8888-999999999999',
    '66666666-7777-8888-9999-000000000000'
);

DELETE FROM workload_action
WHERE id IN (
    'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa',
    'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb',
    'cccccccc-cccc-cccc-cccc-cccccccccccc',
    'dddddddd-dddd-dddd-dddd-dddddddddddd',
    'xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx',
    'yyyyyyyy-yyyy-yyyy-yyyy-yyyyyyyyyyyy',
    '22222222-3333-4444-5555-666666666666'
);

DELETE FROM tuning_parameters
WHERE id IN (1, 2, 3);

DELETE FROM alerts
WHERE pod_id IN (
    '11111111-1111-1111-1111-111111111111',
    '33333333-3333-3333-3333-333333333333',
    '55555555-5555-5555-5555-555555555555'
);

-- Now insert your dummy data as before...

-- alerts table
INSERT INTO alerts (
    alert_type, alert_model, alert_description, pod_id, node_id,
    source_ip, source_port, destination_ip, destination_port, protocol, created_at
) VALUES
('Abnormal', 'ModelA', 'CPU spike', '11111111-1111-1111-1111-111111111111', '22222222-2222-2222-2222-222222222222',
 '10.0.0.1', 8080, '10.0.0.2', 80, 'TCP', '2024-07-31 12:00:00'),
('Network-Attack', 'ModelB', 'Network anomaly', '33333333-3333-3333-3333-333333333333', '44444444-4444-4444-4444-444444444444',
 '192.168.1.10', 443, '192.168.1.20', 443, 'UDP', '2024-07-30 12:00:00'),
('Other', 'ModelC', 'SQL Injection', '55555555-5555-5555-5555-555555555555', '66666666-6666-6666-6666-666666666666',
 NULL, NULL, NULL, NULL, NULL, '2024-07-29 12:00:00');

-- tuning_parameters table
INSERT INTO tuning_parameters (id, output_1, output_2, output_3, alpha, beta, gamma, created_at) VALUES
(1, 1.0, 2.0, 3.0, 0.1, 0.2, 0.3, '2024-07-31 12:00:00'),
(2, 0.0, -1.0, 9999.99, 1.0, 0.0, -0.5, '2024-07-31 11:00:00'),
(3, 3.1415, 2.7182, 0.0, 0.0, 1.0, 1.0, '2024-07-31 10:00:00');

-- workload_action table
INSERT INTO workload_action (
    id, action_type, action_status, action_start_time, action_end_time, action_reason,
    pod_parent_name, pod_parent_type, pod_parent_uid,
    created_pod_name, created_pod_namespace, created_node_name,
    deleted_pod_name, deleted_pod_namespace, deleted_node_name,
    bound_pod_name, bound_pod_namespace, bound_node_name,
    created_at, updated_at
) VALUES
-- Bind, pending
('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', 'bind', 'pending', '2024-07-31 12:00:00', NULL, 'Initial bind',
 'parent-deploy', 'deployment', 'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb',
 'pod-x', 'ns-x', 'node-x',
 NULL, NULL, NULL,
 'pod-x', 'ns-x', 'node-x',
 '2024-07-31 12:00:00', '2024-07-31 12:00:00'
),
-- Create, successful
('bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb', 'create', 'successful', '2024-07-31 11:00:00', '2024-07-31 12:00:00', 'Created pod',
 'parent-rs', 'replicaset', 'cccccccc-cccc-cccc-cccc-cccccccccccc',
 'pod-y', 'ns-y', 'node-y',
 NULL, NULL, NULL,
 'pod-y', 'ns-y', 'node-y',
 '2024-07-31 11:00:00', '2024-07-31 12:00:00'
),
-- Delete, failed
('cccccccc-cccc-cccc-cccc-cccccccccccc', 'delete', 'failed', '2024-07-31 10:00:00', '2024-07-31 11:00:00', 'Delete failed',
 NULL, NULL, NULL,
 NULL, NULL, NULL,
 'pod-z', 'ns-z', 'node-z',
 NULL, NULL, NULL,
 '2024-07-31 10:00:00', '2024-07-31 11:00:00'
),
-- Move, partial
('dddddddd-dddd-dddd-dddd-dddddddddddd', 'move', 'partial', '2024-07-31 12:00:00', NULL, 'Moving pod',
 'parent-sts', 'statefulset', 'eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeee',
 NULL, NULL, NULL,
 NULL, NULL, NULL,
 'pod-w', 'ns-w', 'node-w',
 '2024-07-31 12:00:00', '2024-07-31 12:00:00'
),
-- Swap_x, successful, parent type Job
('xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx', 'swap_x', 'successful', '2024-07-31 12:00:00', '2024-07-31 12:00:00', 'Swapped pods for balancing',
 'parent-job', 'job', 'ffffffff-ffff-ffff-ffff-ffffffffffff',
 'pod-swap', 'ns-swap', 'node-swap',
 'pod-old', 'ns-old', 'node-old',
 'pod-new', 'ns-new', 'node-new',
 '2024-07-31 12:00:00', '2024-07-31 12:00:00'
),
-- Swap_y, successful, parent type Job
('yyyyyyyy-yyyy-yyyy-yyyy-yyyyyyyyyyyy', 'swap_y', 'successful', '2024-07-31 12:00:00', '2024-07-31 12:00:00', 'Swapped pods for balancing',
 'parent-job', 'job', 'ffffffff-ffff-ffff-ffff-ffffffffffff',
 'pod-swap', 'ns-swap', 'node-swap',
 'pod-old', 'ns-old', 'node-old',
 'pod-new', 'ns-new', 'node-new',
 '2024-07-31 12:00:00', '2024-07-31 12:00:00'
),
-- Create, failed, parent type DaemonSet
('11111111-2222-3333-4444-555555555555', 'create', 'failed', '2024-07-31 12:00:00', '2024-07-31 12:00:00', 'Failed to create pod',
 'parent-daemon', 'daemonset', '22222222-3333-4444-5555-666666666666',
 'pod-daemon', 'ns-daemon', 'node-daemon',
 NULL, NULL, NULL,
 NULL, NULL, NULL,
 '2024-07-31 12:00:00', '2024-07-31 12:00:00'
),
-- Delete, pending, parent type CronJob
('22222222-3333-4444-5555-666666666666', 'delete', 'pending', '2024-07-31 12:00:00', NULL, 'Scheduled delete',
 'parent-cron', 'cronjob', '33333333-4444-5555-6666-777777777777',
 NULL, NULL, NULL,
 'pod-cron', 'ns-cron', 'node-cron',
 NULL, NULL, NULL,
 '2024-07-31 12:00:00', '2024-07-31 12:00:00'
);

-- workload_request_decision table
INSERT INTO workload_request_decision (
    id, pod_id, pod_name, namespace, node_id, node_name, is_elastic, queue_name,
    demand_cpu, demand_memory, demand_slack_cpu, demand_slack_memory, decision_status,
    pod_parent_id, pod_parent_name, pod_parent_kind, created_at, deleted_at
) VALUES
('eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeee', '11111111-1111-1111-1111-111111111111', 'pod-x', 'ns-x', '22222222-2222-2222-2222-222222222222', 'node-x', 'successful', 'queue-x',
 2.0, 4096, 0.5, 512, TRUE,
 'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb', 'parent-deploy', 'deployment', '2024-07-31 12:00:00', NULL
),
('ffffffff-ffff-ffff-ffff-ffffffffffff', '33333333-3333-3333-3333-333333333333', 'pod-y', 'ns-y', '44444444-4444-4444-4444-444444444444', 'node-y', 'failed', 'queue-y',
 1.0, 2048, 0.2, 256, FALSE,
 'cccccccc-cccc-cccc-cccc-cccccccccccc', 'parent-rs', 'replicaSet', '2024-07-30 12:00:00', '2024-07-31 12:00:00'
),
('99999999-9999-9999-9999-999999999999', '55555555-5555-5555-5555-555555555555', 'pod-w', 'ns-w', '66666666-6666-6666-6666-666666666666', 'node-w', 'successful', 'queue-z',
 0.0, 0.0, NULL, NULL, TRUE,
 'dddddddd-dddd-dddd-dddd-dddddddddddd', 'parent-sts', 'statefulset', '2024-07-31 12:00:00', NULL
),
('88888888-8888-8888-8888-888888888888', '77777777-7777-7777-7777-777777777777', 'pod-null', 'ns-null', '88888888-8888-8888-8888-888888888888', 'node-null', 'failed', 'queue-null',
 0.0, 0.0, NULL, NULL, FALSE,
 'ffffffff-ffff-ffff-ffff-ffffffffffff', 'parent-null', 'job', '2024-07-31 12:00:00', NULL
),
('33333333-4444-5555-6666-777777777777', '99999999-8888-7777-6666-555555555555', 'pod-daemon', 'ns-daemon', '11111111-2222-3333-4444-555555555555', 'node-daemon', 'successful', 'queue-daemon',
 4.0, 8192, 1.0, 1024, TRUE,
 '11111111-2222-3333-4444-555555555555', 'parent-daemon', 'daemonset', '2024-07-31 12:00:00', NULL
),
('44444444-5555-6666-7777-888888888888', '22222222-3333-4444-5555-666666666666', 'pod-cron', 'ns-cron', '33333333-4444-5555-6666-777777777777', 'node-cron', 'failed', 'queue-cron',
 0.5, 1024, 0.1, 128, FALSE,
 '22222222-3333-4444-5555-666666666666', 'parent-cron', 'cronjob', '2024-07-31 12:00:00', NULL
),
('55555555-6666-7777-8888-999999999999', 'aaaaaaa1-aaaa-aaaa-aaaa-aaaaaaaaaaaa', 'pod-pending-1', 'ns-pending', 'bbbbbbb1-bbbb-bbbb-bbbb-bbbbbbbbbbbb', 'node-pending-1', 'pending', 'queue-pending-1',
 0.5, 512, 0.1, 64, TRUE,
 'ccccccc1-cccc-cccc-cccc-cccccccccccc', 'parent-pending-1', 'deployment', '2024-07-31 12:00:00', NULL
),
('66666666-7777-8888-9999-000000000000', 'aaaaaaa2-aaaa-aaaa-aaaa-aaaaaaaaaaaa', 'pod-pending-2', 'ns-pending', 'bbbbbbb2-bbbb-bbbb-bbbb-bbbbbbbbbbbb', 'node-pending-2', 'pending', 'queue-pending-2',
 1.0, 1024, 0.2, 128, FALSE,
 'ccccccc2-cccc-cccc-cccc-cccccccccccc', 'parent-pending-2', 'statefulset', '2024-07-31 12:00:00', NULL);