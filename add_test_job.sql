-- 添加测试任务数据
INSERT INTO sys_job (job_name, job_group, invoke_target, cron_expression, misfire_policy, concurrent, status, create_by, remark) 
VALUES ('测试任务1', 'DEFAULT', 'test.run_task()', '0 0/10 * * * ?', '3', '1', '0', 'admin', '这是一个测试任务');

INSERT INTO sys_job (job_name, job_group, invoke_target, cron_expression, misfire_policy, concurrent, status, create_by, remark) 
VALUES ('系统监控', 'SYSTEM', 'monitor.check_system()', '0 0/30 * * * ?', '3', '1', '0', 'admin', '系统定时监控任务'); 