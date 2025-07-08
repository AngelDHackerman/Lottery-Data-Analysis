# Database in Glue
resource "aws_glue_catalog_database" "lottery_db" {
  name = "lottery_santalucia_db"
}