package id_check

import (
    "database/sql"
    "log"
)

func Connect() {

    db, err := gorm.Open(sqlite.Open("../example.sql"), &gorm.Config{})

    log.Println("Successfully connected to database and pinged it")
}