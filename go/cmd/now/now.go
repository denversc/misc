package main

import (
	"fmt"
	"time"
)

func main() {
	currentTime := time.Now().UTC()
	formattedTime := currentTime.Format("20060102150405")
	fmt.Println(formattedTime)
}
