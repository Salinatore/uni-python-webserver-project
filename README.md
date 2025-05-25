# Web Server Minimo in Python

Semplice server HTTP multithread sviluppato in Python per il corso di **Programmazione di Reti** (Università di Bologna). Serve contenuti statici su `localhost:8080` gestendo richieste `GET` e rispondendo con codici HTTP standard (`200`, `404`, ecc.).

## Contenuto

- `server.py`: server TCP multithread
- `www/`: HTML/CSS/immagini statiche
- `log.txt`: log delle richieste

## Funzionalità

- Supporto MIME con `mimetypes`
- Logging delle richieste
- Layout responsive lato client
- Codici supportati: `200`, `400`, `404`, `405`, `500`
