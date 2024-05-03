package main

import (
	"fmt"
	"log"
	"math/rand"
	"os"
	"strconv"
)

const ALPHANUMERIC_ALPHABET = "23456789abcdefghjkmnpqrstvwxyz"

func main() {
	parsedArgs, err := parseArgs()
	if err != nil {
		log.Fatalf("ERROR: invalid command-line arguments: %v", err)
	}

	randomString := generateRandomAlphanumericString(parsedArgs.Length)
	fmt.Println(randomString)
}

type ParsedArgs struct {
	Length int
}

func generateRandomAlphanumericString(length int) string {
	if length < 0 {
		panic(fmt.Sprintf("invalid length: %v", length))
	}

	randomChars := ""
	for i := 0; i < length; i++ {
		randomRuneIndex := rand.Intn(len(ALPHANUMERIC_ALPHABET))
		randomRune := ALPHANUMERIC_ALPHABET[randomRuneIndex]
		randomChars = randomChars + string(randomRune)
	}
	return randomChars
}

func parseArgs() (parsedArgs ParsedArgs, err error) {
	err = nil

	args := os.Args[1:]
	if len(args) == 0 {
		parsedArgs.Length = 10
	} else if len(args) > 1 {
		err = fmt.Errorf("unexpected argument: %v", args[1])
	} else {
		lengthString := args[0]
		parsedArgs.Length, err = strconv.Atoi(lengthString)
		if err != nil {
			err = fmt.Errorf("invalid length: %v (%w)", lengthString, err)
		} else if parsedArgs.Length < 0 {
			err = fmt.Errorf("invalid length: %v (must be greater than or equal to 0)", lengthString)
		}
	}

	return
}
