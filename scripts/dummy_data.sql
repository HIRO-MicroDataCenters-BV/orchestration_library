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
    '66666666-7777-8888-9999-000000000000',
    '11aa11aa-11aa-11aa-11aa-11aa11aa11aa',
    '22bb22bb-22bb-22bb-22bb-22bb22bb22bb',
    '33cc33cc-33cc-33cc-33cc-33cc33cc33cc',
    '44dd44dd-44dd-44dd-44dd-44dd44dd44dd',
    '55ee55ee-55ee-55ee-55ee-55ee55ee55ee',
    '66ff66ff-66ff-66ff-66ff-66ff66ff66ff'
);

DELETE FROM workload_action
WHERE id IN (
    'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa',
    'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb',
    'cccccccc-cccc-cccc-cccc-cccccccccccc',
    'dddddddd-dddd-dddd-dddd-dddddddddddd',
    '12345678-1234-1234-1234-123456789abc',
    '77777777-7777-7777-7777-777777777777',
    '11111111-2222-3333-4444-555555555555',
    '22222222-3333-4444-5555-666666666666',
    'aa11aa11-aa11-aa11-aa11-aa11aa11aa11',
    'bb22bb22-bb22-bb22-bb22-bb22bb22bb22',
    'cc33cc33-cc33-cc33-cc33-cc33cc33cc33',
    'dd44dd44-dd44-dd44-dd44-dd44dd44dd44',
    'ee55ee55-ee55-ee55-ee55-ee55ee55ee55',
    'ff66ff66-ff66-ff66-ff66-ff66ff66ff66'
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
('bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb', 'create', 'succeeded', '2024-07-31 11:00:00', '2024-07-31 12:00:00', 'Created pod',
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
-- Move, pending
('dddddddd-dddd-dddd-dddd-dddddddddddd', 'move', 'pending', '2024-07-31 12:00:00', NULL, 'Moving pod',
 'parent-sts', 'statefulset', 'eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeee',
 NULL, NULL, NULL,
 NULL, NULL, NULL,
 'pod-w', 'ns-w', 'node-w',
 '2024-07-31 12:00:00', '2024-07-31 12:00:00'
),
-- Swap_x, successful, parent type Job
('12345678-1234-1234-1234-123456789abc', 'swap_x', 'succeeded', '2024-07-31 12:00:00', '2024-07-31 12:00:00', 'Swapped pods for balancing',
 'parent-job', 'job', 'ffffffff-ffff-ffff-ffff-ffffffffffff',
 'pod-swap', 'ns-swap', 'node-swap',
 'pod-old', 'ns-old', 'node-old',
 'pod-new', 'ns-new', 'node-new',
 '2024-07-31 12:00:00', '2024-07-31 12:00:00'
),
-- Swap_y, successful, parent type Job
('77777777-7777-7777-7777-777777777777', 'swap_y', 'succeeded', '2024-07-31 12:00:00', '2024-07-31 12:00:00', 'Swapped pods for balancing',
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
    pod_parent_id, pod_parent_name, pod_parent_kind, action_type, decision_start_time, decision_end_time, created_at, deleted_at
) VALUES
('eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeee', '11111111-1111-1111-1111-111111111111', 'pod-x', 'ns-x', '22222222-2222-2222-2222-222222222222', 'node-x', FALSE, 'queue-x',
 2.0, 4096, 0.5, 512, 'successful',
 'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb', 'parent-deploy', 'deployment', 'create', '2024-07-31 12:00:00', '2024-07-31 12:00:01', '2024-07-31 12:00:00', NULL
),
('ffffffff-ffff-ffff-ffff-ffffffffffff', '33333333-3333-3333-3333-333333333333', 'pod-y', 'ns-y', '44444444-4444-4444-4444-444444444444', 'node-y', FALSE, 'queue-y',
 1.0, 2048, 0.2, 256, 'failed',
 'cccccccc-cccc-cccc-cccc-cccccccccccc', 'parent-rs', 'replicaset', 'bind', '2024-07-31 12:00:00', '2024-07-31 12:00:01', '2024-07-30 12:00:00', '2024-07-31 12:00:00'
),
('99999999-9999-9999-9999-999999999999', '55555555-5555-5555-5555-555555555555', 'pod-w', 'ns-w', '66666666-6666-6666-6666-666666666666', 'node-w', TRUE, 'queue-z',
 0.0, 0.0, NULL, NULL, 'successful',
 'dddddddd-dddd-dddd-dddd-dddddddddddd', 'parent-sts', 'statefulset', 'create', '2024-07-31 12:00:00', '2024-07-31 12:00:01', '2024-07-31 12:00:00', NULL
),
('88888888-8888-8888-8888-888888888888', '77777777-7777-7777-7777-777777777777', 'pod-null', 'ns-null', '88888888-8888-8888-8888-888888888888', 'node-null', FALSE, 'queue-null',
 0.0, 0.0, NULL, NULL, 'failed',
 'ffffffff-ffff-ffff-ffff-ffffffffffff', 'parent-null', 'job', 'create', '2024-07-31 12:00:00', '2024-07-31 12:00:01', '2024-07-31 12:00:00', NULL
),
('33333333-4444-5555-6666-777777777777', '99999999-8888-7777-6666-555555555555', 'pod-daemon', 'ns-daemon', '11111111-2222-3333-4444-555555555555', 'node-daemon', TRUE, 'queue-daemon',
 4.0, 8192, 1.0, 1024, 'successful',
 '11111111-2222-3333-4444-555555555555', 'parent-daemon', 'daemonset', 'bind', '2024-07-31 12:00:00', '2024-07-31 12:00:01', '2024-07-31 12:00:00', NULL
),
('44444444-5555-6666-7777-888888888888', '22222222-3333-4444-5555-666666666666', 'pod-cron', 'ns-cron', '33333333-4444-5555-6666-777777777777', 'node-cron', FALSE, 'queue-cron',
 0.5, 1024, 0.1, 128, 'failed',
 '22222222-3333-4444-5555-666666666666', 'parent-cron', 'cronjob', 'bind', '2024-07-31 12:00:00', '2024-07-31 12:00:01', '2024-07-31 12:00:00', NULL
),
('55555555-6666-7777-8888-999999999999', 'aaaaaaa1-aaaa-aaaa-aaaa-aaaaaaaaaaaa', 'pod-pending-1', 'ns-pending', 'bbbbbbb1-bbbb-bbbb-bbbb-bbbbbbbbbbbb', 'node-pending-1', TRUE, 'queue-pending-1',
 0.5, 512, 0.1, 64, 'pending',
 'ccccccc1-cccc-cccc-cccc-cccccccccccc', 'parent-pending-1', 'deployment', 'bind', '2024-07-31 12:00:00', '2024-07-31 12:00:01', '2024-07-31 12:00:00', NULL
),
('66666666-7777-8888-9999-000000000000', 'aaaaaaa2-aaaa-aaaa-aaaa-aaaaaaaaaaaa', 'pod-pending-2', 'ns-pending', 'bbbbbbb2-bbbb-bbbb-bbbb-bbbbbbbbbbbb', 'node-pending-2', FALSE, 'queue-pending-2',
 1.0, 1024, 0.2, 128, 'pending',
 'ccccccc2-cccc-cccc-cccc-cccccccccccc', 'parent-pending-2', 'statefulset', 'bind', '2024-07-31 12:00:00', '2024-07-31 12:00:01', '2024-07-31 12:00:00', NULL);


 -- Insert workload_action rows (IDs all new)
INSERT INTO workload_action (
  id, action_type, action_status, action_start_time, action_end_time, action_reason,
  pod_parent_name, pod_parent_type, pod_parent_uid,
  created_pod_name, created_pod_namespace, created_node_name,
  deleted_pod_name, deleted_pod_namespace, deleted_node_name,
  bound_pod_name, bound_pod_namespace, bound_node_name,
  created_at, updated_at
) VALUES
-- BIND
('aa11aa11-aa11-aa11-aa11-aa11aa11aa11','bind','pending','2025-09-17 10:00:00',NULL,'Bind test',
 'parent-deploy','deployment','puid-bind-1111',
 NULL,NULL,NULL,
 NULL,NULL,NULL,
 'bind-pod','bind-ns','bind-node',
 '2025-09-17 10:00:00','2025-09-17 10:00:00'),
-- CREATE (join uses created_node_name per current repo logic)
('bb22bb22-bb22-bb22-bb22-bb22bb22bb22','create','succeeded','2025-09-17 11:00:00','2025-09-17 11:05:00','Create test',
 'parent-rs','replicaset','puid-create-2222',
 'create-pod','create-ns','create-node',
 NULL,NULL,NULL,
 NULL,NULL,NULL,
 '2025-09-17 11:00:00','2025-09-17 11:05:00'),
-- DELETE
('cc33cc33-cc33-cc33-cc33-cc33cc33cc33','delete','pending','2025-09-17 12:00:00',NULL,'Delete test',
 'parent-sts','statefulset','puid-delete-3333',
 NULL,NULL,NULL,
 'delete-pod','delete-ns','delete-node',
 NULL,NULL,NULL,
 '2025-09-17 12:00:00','2025-09-17 12:00:00'),
-- MOVE (join uses created_pod_name)
('dd44dd44-dd44-dd44-dd44-dd44dd44dd44','move','pending','2025-09-17 13:00:00',NULL,'Move test',
 'parent-sts','statefulset','puid-move-4444',
 'move-pod','move-ns','move-node',
 NULL,NULL,NULL,
 NULL,NULL,NULL,
 '2025-09-17 13:00:00','2025-09-17 13:00:00'),
-- SWAP_X (join uses created_node_name)
('ee55ee55-ee55-ee55-ee55-ee55ee55ee55','swap_x','succeeded','2025-09-17 14:00:00','2025-09-17 14:05:00','Swap X test',
 'parent-job','job','puid-swapx-5555',
 'swapx-pod','swapx-ns','swapx-node',
 NULL,NULL,NULL,
 NULL,NULL,NULL,
 '2025-09-17 14:00:00','2025-09-17 14:05:00'),
-- SWAP_Y (join uses created_node_name)
('ff66ff66-ff66-ff66-ff66-ff66ff66ff66','swap_y','succeeded','2025-09-17 15:00:00','2025-09-17 15:05:00','Swap Y test',
 'parent-job','job','puid-swapy-6666',
 'swapy-pod','swapy-ns','swapy-node',
 NULL,NULL,NULL,
 NULL,NULL,NULL,
 '2025-09-17 15:00:00','2025-09-17 15:05:00');

-- Insert workload_request_decision rows (IDs all new)
-- Ensure pod_name / namespace / node_name match join rules for each action_type
INSERT INTO workload_request_decision (
  id, pod_id, pod_name, namespace, node_id, node_name, is_elastic, queue_name,
  demand_cpu, demand_memory, demand_slack_cpu, demand_slack_memory, decision_status,
  pod_parent_id, pod_parent_name, pod_parent_kind, action_type,
  decision_start_time, decision_end_time, created_at, deleted_at
) VALUES
-- BIND: matches bound_* in action
('11aa11aa-11aa-11aa-11aa-11aa11aa11aa','bind-pod-id','bind-pod','bind-ns','bind-node-id','bind-node',FALSE,'queue-bind',
 1.0,512,0.1,64,'successful',
 'puid-bind-1111','parent-deploy','deployment','bind',
 '2025-09-17 10:00:00',NULL,'2025-09-17 10:00:00',NULL),
-- CREATE: pod_name must equal created_node_name per current code
('22bb22bb-22bb-22bb-22bb-22bb22bb22bb','create-pod-id','create-node','create-ns','create-node-id','create-node',FALSE,'queue-create',
 2.0,1024,0.2,128,'successful',
 'puid-create-2222','parent-rs','replicaset','create',
 '2025-09-17 11:00:00',NULL,'2025-09-17 11:00:00',NULL),
-- DELETE: matches deleted_* in action
('33cc33cc-33cc-33cc-33cc-33cc33cc33cc','delete-pod-id','delete-pod','delete-ns','delete-node-id','delete-node',FALSE,'queue-delete',
 0.5,256,0.05,32,'failed',
 'puid-delete-3333','parent-sts','statefulset','delete',
 '2025-09-17 12:00:00',NULL,'2025-09-17 12:00:00',NULL),
-- MOVE: matches created_pod_name / namespace / node_name (created_pod_namespace not in model, so we reuse 'move-ns')
('44dd44dd-44dd-44dd-44dd-44dd44dd44dd','move-pod-id','move-pod','move-ns','move-node-id','move-node',TRUE,'queue-move',
 1.5,768,0.15,96,'pending',
 'puid-move-4444','parent-sts','statefulset','move',
 '2025-09-17 13:00:00',NULL,'2025-09-17 13:00:00',NULL),
-- SWAP_X: pod_name equals created_node_name
('55ee55ee-55ee-55ee-55ee-55ee55ee55ee','swapx-pod-id','swapx-node','swapx-ns','swapx-node-id','swapx-node',TRUE,'queue-swapx',
 2.5,1536,0.25,160,'successful',
 'puid-swapx-5555','parent-job','job','swap_x',
 '2025-09-17 14:00:00',NULL,'2025-09-17 14:00:00',NULL),
-- SWAP_Y: pod_name equals created_node_name
('66ff66ff-66ff-66ff-66ff-66ff66ff66ff','swapy-pod-id','swapy-node','swapy-ns','swapy-node-id','swapy-node',TRUE,'queue-swapy',
 3.0,2048,0.3,192,'successful',
 'puid-swapy-6666','parent-job','job','swap_y',
 '2025-09-17 15:00:00',NULL,'2025-09-17 15:00:00',NULL);

 