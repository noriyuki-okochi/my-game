drop table if exists pattern;
create table if not exists pattern( pt_id text NOT NULL, 
                                    pos1 text NOT NULL,
                                    col1 text NOT NULL,
                                    pos2 text NOT NULL,
                                    col2 text NOT NULL,
                                    pos3 text NOT NULL,
                                    col3 text NOT NULL,
                                    inserted_at TIMESTAMP DEFAULT(DATETIME('now','localtime')),
                                    PRIMARY KEY(pt_id)
                                );
drop table if exists solution;
create table if not exists solution( pt_id text NOT NULL,
                                     sl_no integer NOT NULL,
                                     sl_st integer DEFAULT(0),
                                     cmd text,
                                     inserted_at TIMESTAMP DEFAULT(DATETIME('now','localtime')),
                                     PRIMARY KEY(pt_id,sl_no)
                                );
