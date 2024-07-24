#!/usr/bin/env bash

# Автоматический установщик для сервера линукс веб-приложения при помощи dockerhub и установкой уже с готовым архивом. Помимо этого также есть возможность настроить HTTPS и поднять swarm.
# Ссылки на докерхаб, пути к приложению были скрыты специально.

echo "Каким образом вы хотите загрузить сервер [название приложения]?
1. Выгрузка при помощи DockerHub
2. Установка с уже имеющимся архивом"
read -p 'Введите номер варианта ответа: ' installparametr

if [ $installparametr -eq 1 ]; then
	read -p 'Введите номер сборки [название приложения] (Номер свежей сборки: d221101)' app_ver
	docker pull [ссылка на приложение]:$app_ver
elif [ $installparametr -eq 2 ]; then
	archives_path="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
	archive_name=$(find -type f -name -iname "*docker_app*.tar.gz")
	archive_name=$(archive_name:2)
	TarGzProceset="$archives_path/$archive_name"
	echo "Распаковываем архив..."
	gunzip $TarGzProceset
	echo "Загружаем данные архивa в Docker..."
	archive_tar_name=$(find -type f -name -iname "*docker_app*.tar")
	archive_tar_name=$(archive_tar_name:2)
	TarProceset="$archive_path/$archives_tar_name"
	docker load < $TarAPP
	proceset_ver=${archive_tar_name#docker_app}
	proceset_ver=${app_ver%.tar}
else
	echo "Ошибка, вы неправильно выбрали номер варианта."
fi

#====================================================================================================

# Имя docker сервиса
ServiceName="app"

# Функция для создания томов (volume)
function CreateVolume {
	sudo docker volume create app-data
	echo "Создание тома app-data"
	sudo docker volume create app-log
	echo "Создание тома  app-log"
}

# Функция для запуска Docker Swarm
function SwarmInit {
	sudo docker swarm init --advertise-addr 127.0.0.1:2377 --listen-addr 127.0.0.1:2377
}

echo "Сделать настройку серверу по HTTPS?
1. Да
2. Нет"

read -p "Введите номер варианта ответа: " HTTPSparametr

#Условие для проверки пункта по установке HTTPS и настройке ОЗУ+ЦПУ
if [ $HTTPSparametr -eq 1 ]; then
    read -p "Укажите путь до файла PKCS#12(*.pfx) c указанием также файла:" pfx_file_path
    read -p "Укажите пароль к файлу PKCS#12(*.pfx):" pfx_password
	echo "Ввести параметры по ограничению ОЗУ и ЦПУ?
	1. Да
	2. Нет"
	read -p "Введите номер варианта ответа: " cpu_and_ram_params
elif [ $HTTPSparametr -eq 2 ]; then
	echo "Пропускаем настройку HTTPS..."
else
	echo "Ошибка, вы неправильно выбрали номер варианта."
fi


if [$cpu_and_ram_params -eq 1]; then
	echo "Хотите вести свои значения? (Если нет, тогда будут использоваться значения по умолчанию)
1. Да	
2. Нет"
	read -p "Введите номер варианта ответа: " defaultparams
else
	true
fi

if [ $defaultparams -eq 2 ]; then
	limit_ram=$(--limit-memory 30G)
	limit_cpu=$(--limit-cpu 2)
elif [ $defaultparams -eq 1 ]; then
	read -p "Введите количество потоков ядра: " cpu_size
	read -p "Введите количество выделяемой памяти в гигабайтах: " ram_size
	limit_ram="--limit-memory $cpu_size"G""
	limit_cpu="--limit-cpu $ram_size"
else
	echo "Ошибка, вы неправильно выбрали номер варианта."
fi

# Функция для запуска сервиса по HTTPS
function HTTPAppStart {
	docker run --name=$ServiceName \
	--mount source=app-data,target=/var/lib/app/data/ \
	--mount source=app-log,target=/var/log/app/ \
	-p 0.0.0.0:8010:8010 -d --restart=always \
	[путь к приложению]:$app_ver
}

function HTTPsSwarmServiceStart {
	docker secret create app_https_certificate $pfx_file_path
	echo -n "$pfx_password" | docker secret create app_https_certificate_password -
	docker service create --name $ServiceName \
	--secret app_https_certificate \
	--secret app_https_certificate_password \
	--mount type=volume,src=app-data,target=/var/lib/app/data/ \
	--mount type=volume,src=app-log,target=/var/log/app/ \
	--publish published=8010,target=8010,mode=host \
	$limit_ram \
	$limit_cpu \
	--restart-max-attempts 5 \
	--restart-condition "on-failure" \
	[путь к приложению]:$app_ver
}

function isSwarmNode(){
    if [ "$(docker info | grep Swarm | sed 's/Swarm: //g')" == "inactive" ]; then
        $isSWARMnode=false;
    else
        $isSWARMNode=true;
    fi
}

# Настройка HTTPs с docker swarm 
if [ $isSwarmNode=false ] && [ $HTTPSparametr -eq 1 ]; then
	HTTPsSwarmServiceStart
elif [ $isSwarmNode=true ] && [ $HTTPSparametr -eq 1 ]; then
	echo "Невозможно воспользоваться Docker Swarm. Данный узел уже выступает менеджером."
else
	true
fi

# Настройка HTTP
if [ $HTTPSparametr -eq 2 ]; then
	HTTPAppStart
else
	true
fi

