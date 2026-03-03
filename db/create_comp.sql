drop table if exists comp_pattern;
create table if not exists comp_pattern( entry_no integer primary key autoincrement, 
                                    pos1 text NOT NULL,
                                    col1 text NOT NULL,
                                    pos2 text NOT NULL,
                                    col2 text NOT NULL,
                                    pos3 text NOT NULL,
                                    col3 text NOT NULL,
                                    pitch INTEGER,
                                    roll INTEGER,
                                    inserted_at TIMESTAMP DEFAULT(DATETIME('now','localtime'))
                                );
