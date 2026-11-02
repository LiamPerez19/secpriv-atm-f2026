module atm/runner

go 1.27.3

replace atm/id_check => ../id_check

require atm/id_check v0.0.0-00010101000000-000000000000

require (
	filippo.io/edwards25519 v1.2.0 // indirect
	github.com/go-sql-driver/mysql v1.10.1 // indirect
)
