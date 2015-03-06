import re

def parse(file):
  NOTES = 1
  DATA = 2
  state = NOTES
  
  notes = []
  data = []
  
  for row in file:
    row = row.strip()
    if not row:
      continue
    if state == NOTES:
      if re.match('^Date', row):
        state = DATA
      else:
        notes.append(row)
    elif state == DATA:
      data.append(row.split(','))
    
  return {
    'notes': notes,
    'data': data
  }   