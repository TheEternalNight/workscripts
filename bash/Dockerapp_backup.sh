#!/bin/bash

# Бэкап данных при помощи bash скрипта для докер-приложения. Все имена продуктов компании скрыты.

trap 'echo "# $BASH_COMMAND";read' DEBUG
# Set docker service name
ServiceName="app-clickhouse"
# Set docker service create command option
ServiceOption="--quiet --app_user --secret app_user_password_hash --secret external_user --secret external_user_password_hash --secret clickhouse_dhparam.pem --secret clickhouse.crt --secret clickhouse.key --publish published=8123,target=8123,mode=host --mount type=volume,src=app-clickhouse,target=/var/lib/clickhouse/ --mount type=volume,src=app-clickhouse-log,target=/var/log/clickhouse-server --restart-max-attempts 5 --restart-condition "on-failure""
# Set docker volume with data on host machine
VolumeDir="/var/lib/docker/volumes/app-clickhouse"
# Set path for backup
BackupDir="/bkp"
# Set path for script logs
LogPath="/путь_до_лога/script-log.txt"

# Get used docker image name
ImageName=$(docker service inspect --format='{{.Spec.TaskTemplate.ContainerSpec.Image}}' $ServiceName | sed -r 's/@.+//')

# Docker service stop function
function ServiceStop {
docker service rm $ServiceName
}
# Docker service start function
function ServiceStart {
docker service create --name $ServiceName $ServiceOption $ImageName
}
# Make data miracle function
function MakeMiracle {
rsync -az --delete $VolumeDir $BackupDir
}
# Run
if test -f "$LogPath"
then
echo "Log file exists."
else
touch $LogPath
fi

if ServiceStop
then 
sleep 1s; date "+%d-%m-%Y-%H-%M-%S" >> $LogPath; MakeMiracle >> $LogPath; ServiceStart >> $LogPath
else
echo "Service $ServiceName is not exist. Backup is not created." >> $LogPath
fi
