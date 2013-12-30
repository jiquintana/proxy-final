#!/bin/bash
cat << EOF | sqlite3 proxy.db -echo -init -
update user set L_AH=0 where uid=1;
update user set M_AH=0 where uid=1;
update user set X_AH=0 where uid=1;
update user set J_AH=0 where uid=1;
update user set V_AH=0 where uid=1;
update user set S_AH=0 where uid=1;
update user set D_AH=0 where uid=1;
update user set description='pepito' where uid=1;
select * from user where uid=1;
.quit
EOF 
