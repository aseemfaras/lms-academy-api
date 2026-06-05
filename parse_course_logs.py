import re

log_file = 'C:\\aideas\\lms-backend\\sql_queries.log'
insert_pattern = re.compile(r'INSERT INTO "courses" (.+?) VALUES (.+?);')
delete_pattern = re.compile(r'DELETE FROM "courses" WHERE (.+?);')

with open(log_file, 'r') as f:
    for line in f:
        if insert_pattern.search(line) or delete_pattern.search(line):
            print(line.strip())
