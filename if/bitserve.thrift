
enum LoadType {
  STRING = 1,
  CENTS_FLOAT = 2,
  JOINED_INTS = 3,
  INT = 4
}

struct LoadColumn {
  1:bool is_primary_key=0
  2:string name
  3:LoadType type = STRING
}

exception NoSuchTableException {
}

exception ParseException {
  1:string message
}

service BitServe {

  i32 load_table(1:string name, 2:string path, 3:list<LoadColumn> columns)
  
  list<i32> query(1:string table,
                  2:string query) throws (1:NoSuchTableException nste,
                                          2:ParseException pe)

}