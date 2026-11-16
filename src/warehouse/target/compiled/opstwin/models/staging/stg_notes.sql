select ticket_id, note_text
from read_json(
    'data/bronze/maintenance_notes/notes.jsonl',
    format = 'newline_delimited',
    columns = {ticket_id: 'VARCHAR', note_text: 'VARCHAR'}
)