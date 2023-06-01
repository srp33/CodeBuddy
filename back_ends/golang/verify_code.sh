mv "$1" verification_code.go
go build -o verification_code verification_code.go

./verification_code