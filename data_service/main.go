package main

import (
    "net/http"
    "github.com/gin-gonic/gin"
)

type expense struct {
	GdriveID string `json:"gdrive_id"`
	BusinessName string `json:"business_name"`
	Date string `json:"date"`
	Total float64 `json:"total"`
	Category string `json:"category"`
}

var expenses = []expense {
	{ GdriveID: "1", BusinessName: "Starbucks", Date: "01/01/1960", Total: 5.50, Category: "Food" },
	{ GdriveID: "2", BusinessName: "ODEON", Date: "02/01/1960", Total: 10.00, Category: "Entertaiment" },
	{ GdriveID: "3", BusinessName: "Tesco", Date: "03/01/1960", Total: 15.99, Category: "Shopping" },
}

func getExpenses(c *gin.Context) {
	c.IndentedJSON(http.StatusOK, expenses)
}

func postEditedExpense(c *gin.Context) {
	var newExpense expense

	if err := c.BindJSON(&newExpense); err != nil {
		return
	}

	expenses = append(expenses, newExpense)
	c.IndentedJSON(http.StatusCreated, newExpense)
}

func main() {
	router := gin.Default()
	router.GET("/api/expenses", getExpenses)
	router.POST("/api/expenses", postEditedExpense)
	router.Run("localhost:8080")
}