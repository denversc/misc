package main

import (
	"bufio"
	"fmt"
	"os"
	"strings"
)
import "path/filepath"

func main() {
	err := run(os.Args[1:])
	if err != nil {
		fmt.Println("ERROR:", err)
		os.Exit(1)
	}
}

func run(args []string) error {
	ch := generatePaths(args)

	for pathOrError := range ch {
		if pathOrError.Error != nil {
			return pathOrError.Error
		}
		fmt.Println(absPathFromPath(pathOrError.Path))
	}

	return nil
}

type pathOrError struct {
	Path  string
	Error error
}

func generatePaths(args []string) chan *pathOrError {
	ch := make(chan *pathOrError)

	go func() {
		defer close(ch)
		if len(args) > 0 {
			for _, arg := range args {
				ch <- &pathOrError{Path: arg}
			}
		} else {
			scanner := bufio.NewScanner(os.Stdin)
			for scanner.Scan() {
				line := scanner.Text()
				line = strings.TrimSpace(line)
				ch <- &pathOrError{Path: line}
			}
			if err := scanner.Err(); err != nil {
				ch <- &pathOrError{Error: err}
			}
		}
	}()

	return ch
}

func absPathFromPath(path string) string {
	pathAbs, err := filepath.Abs(path)
	if err != nil {
		pathAbs = path
	}
	return filepath.Clean(pathAbs)
}
