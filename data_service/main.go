package main

import (
	"os"
    "net/http"
    "github.com/gin-gonic/gin"
	"golang.org/x/oauth2/google"
	"google.golang.org/api/sheets/v4"
	"google.golang.org/api/option"
	"encoding/base64"
	"io/ioutil"
	"fmt"
	"context"
	"log"
)

type expense struct {
	GdriveID string `json:"gdrive_id"`
	BusinessName string `json:"business_name"`
	Date string `json:"date"`
	Total float64 `json:"total"`
	Category string `json:"category"`
	SpreadsheetId string `json:"spreadsheet_id"`
	SheetId int `json:"sheet_id"`
}

var expenses = []expense {
	{ GdriveID: "1", BusinessName: "Starbucks", Date: "01/01/1960", Total: 5.50, Category: "Food", SpreadsheetId: "1", SheetId: 0 },
	{ GdriveID: "2", BusinessName: "ODEON", Date: "02/01/1960", Total: 10.00, Category: "Entertaiment", SpreadsheetId: "1", SheetId: 0 },
	{ GdriveID: "3", BusinessName: "Tesco", Date: "03/01/1960", Total: 15.99, Category: "Shopping", SpreadsheetId: "1", SheetId: 0 },
}

func getExpenses(c *gin.Context) {
	c.IndentedJSON(http.StatusOK, expenses)
}

func postEditedExpense(c *gin.Context) {
	var newExpense expense

	if err := c.BindJSON(&newExpense); err != nil {
		return
	}

	ctx := context.Background()

	// get bytes from base64 encoded google service accounts key
	credBytes, err := base64.StdEncoding.DecodeString(os.Getenv("KEY_JSON_BASE64"))
	if err != nil {
		log.Fatalf("%v", err)
		return
	}

	// authenticate and get configuration
	config, err := google.JWTConfigFromJSON(credBytes, "https://www.googleapis.com/auth/spreadsheets")
	if err != nil {
		log.Fatalf("%v", err)
		return
	}

	// create client with config and context
	client := config.Client(ctx)

	// create new service using client
	srv, err := sheets.NewService(ctx, option.WithHTTPClient(client))
	if err != nil {
		log.Fatalf("%v", err)
		return
	}

	spreadsheetId := newExpense.SpreadsheetId
	sheetId := newExpense.SheetId

	response1, err := srv.Spreadsheets.Get(spreadsheetId).Fields("sheets(properties(sheetId,title))").Do()
	if err != nil || response1.HTTPStatusCode != 200 {
		log.Fatalf("%v", err)
		return
	}

	sheetName := ""
	for _, v := range response1.Sheets {
		prop := v.Properties
		if prop.SheetId == int64(sheetId) {
			sheetName = prop.Title
			break
		}
	}

	row := &sheets.ValueRange{
		Values: [][]interface{}{{newExpense.GdriveID, newExpense.BusinessName, newExpense.Date, newExpense.Total, newExpense.Category}},
	}

	response2, err := srv.Spreadsheets.Values.Append(spreadsheetId, sheetName, row).ValueInputOption("USER_ENTERED").InsertDataOption("INSERT_ROWS").Context(ctx).Do()
	if err != nil || response2.HTTPStatusCode != 200 {
		log.Fatalf("%v", err)
		return
	}

	expenses = append(expenses, newExpense)
	c.IndentedJSON(http.StatusCreated, newExpense)
}

func encode_cred(cred_file_name string) {
	currentDir, err := os.Getwd()
	cred_file := fmt.Sprintf("%s/%s", currentDir, cred_file_name)
	fileContent, err := ioutil.ReadFile(cred_file)
	if err != nil {
		panic(err)
	}

	// Convert to base64
	base64Data := base64.StdEncoding.EncodeToString(fileContent)

	key := "KEY_JSON_BASE64"

	// Export variable
	os.Setenv(key, base64Data)
}

func main() {
	encode_cred("sa.json")
	router := gin.Default()
	router.GET("/api/expenses", getExpenses)
	router.POST("/api/expenses", postEditedExpense)
	router.Run("localhost:8080")
}