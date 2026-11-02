package main
import (
	"fmt"
	"atm/id_check"
)

func multiply(a, b int) int {
	return a * b
}

func main() {
	result := multiply(5, 10)
	fmt.Println(result)

	id_check.Connect()
}