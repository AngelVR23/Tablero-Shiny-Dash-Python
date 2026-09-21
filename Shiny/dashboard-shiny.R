library(shiny)
library(bslib)
library(bsicons)
library(ggplot2)
library(plotly)
library(dplyr)

# Cargar datos
# Asumiendo que tips.csv está en la misma carpeta
tips <- read.csv("tips.csv")

# Pre-cálculo para el slider
bill_rng <- list(
  min = min(tips$total_bill, na.rm = TRUE),
  max = max(tips$total_bill, na.rm = TRUE)
)

# UI (Interfaz de usuario)
ui <- page_sidebar(
  title = "Restaurant tipping",
  fillable = TRUE,
  
  sidebar = sidebar(
    sliderInput(
      "total_bill",
      "Bill amount",
      min = bill_rng$min,
      max = bill_rng$max,
      value = c(bill_rng$min, bill_rng$max),
      pre = "$"
    ),
    checkboxGroupInput(
      "time",
      "Food service",
      choices = c("Lunch", "Dinner"),
      selected = c("Lunch", "Dinner"),
      inline = TRUE
    ),
    actionButton("reset", "Reset filter", class = "btn-outline-secondary")
  ),
  
  # Fila de Value Boxes
  layout_columns(
    value_box(
      title = "Total tippers",
      value = textOutput("total_tippers"),
      showcase = bs_icon("person")
    ),
    value_box(
      title = "Average bill",
      value = textOutput("average_bill"),
      showcase = bs_icon("currency-dollar")
    )
  ),
  
  # Fila de Tabla y Gráfico
  layout_columns(
    card(
      card_header("Tips data"),
      tableOutput("table"),
      full_screen = TRUE
    ),
    card(
      card_header(
        "Total bill vs tip",
        popover(
          bs_icon("three-dots"),
          radioButtons(
            "scatter_color",
            NULL,
            choices = c("none", "sex", "smoker", "day", "time"),
            inline = TRUE
          ),
          title = "Add a color variable",
          placement = "top"
        ),
      ),
      plotlyOutput("scatterplot")
    )
  )
)

# Server (Lógica)
server <- function(input, output, session) {
  
  # Reactivo para filtrar datos (el equivalente a tips_data())
  tips_filtered <- reactive({
    tips %>%
      filter(
        total_bill >= input$total_bill[1],
        total_bill <= input$total_bill[2],
        time %in% input$time
      )
  })
  
  output$total_tippers <- renderText({
    nrow(tips_filtered())
  })
  
  output$average_bill <- renderText({
    d <- mean(tips_filtered()$total_bill, na.rm = TRUE)
    if (!is.nan(d)) {
      paste0("$", format(round(d, 2)))
    } else {
      "N/A"
    }
  })
  
  output$table <- renderTable({
    tips_filtered()
  })
  
  output$scatterplot <- renderPlotly({
    color_var <- if (input$scatter_color == "none") NULL else input$scatter_color
    
    p <- ggplot(tips_filtered(), aes(x = total_bill, y = tip, color = .data[[color_var]])) +
      geom_point() +
      geom_smooth(method = "loess", formula = y ~ x) +
      theme_minimal()
    
    # Si no hay color, quitamos la leyenda de 'NULL'
    if (input$scatter_color == "none") {
      p <- ggplot(tips_filtered(), aes(x = total_bill, y = tip)) +
        geom_point() +
        geom_smooth(method = "loess", formula = y ~ x) +
        theme_minimal()
    }
    
    ggplotly(p)
  })
  
  # Evento para resetear filtros
  observeEvent(input$reset, {
    updateSliderInput(session, "total_bill", value = c(bill_rng$min, bill_rng$max))
    updateCheckboxGroupInput(session, "time", selected = c("Lunch", "Dinner"))
  })
}

shinyApp(ui, server)