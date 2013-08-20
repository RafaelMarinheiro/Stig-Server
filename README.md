Stig Server
===========

O servidor do Stig fornece uma API REST que permite acessar os diversos recursos do sistema.

Os principais dados do Stig são:
* Locais
* Usuários
* Comentários

Usuários podem fazer check-in em um local. O histórico de check-ins deve ser armazenado. Usuários podem fazer comentários associados à locais. Os comentários podem ser replies à outros comentários. Um comentário pode possuir um conjunto de Stickers associado.

Pode-se consultar:
* Quais os locais próximos à mim?
* Quais os comentários associados à um local?
* Quais os comentários associados à um comentário?
* Qual o histórico de check-ins de um usuário?
* Etc...

Documentação
============

> Essa específicação é muito prematura. Ela está sujeita à um grande número de modificações

TODA requisição à API será autenticada via basic auth com HTTPS. Quando o usuário em questão for um usuário do Facebook, o usuário será o `userid` e a senha será o `access-token`. A localização do usuário será passado no header `Geolocation`

Acessando recursos
------------------------------------------

### Local

#### Ver local
A cada local está associado um campo identificador. Para acessar um local, deve-se fazer uma requisição GET:
```
GET https://api.stigapp.co/places/<ID-LOCAL>
```

Em caso de sucesso, o servidor retornará uma resposta HTTP com código 200 (OK) retornando um JSON no seguinte formato:

```
{
	"id": <ID-LOCAL>,
	"name": <NOME-DO-LOCAL>,
	"image": <URL-DA-IMAGEM-DO-LOCAL>,
	"description": <DESCRICAO>,
	"location": {
					"lat": <LATITUDE>,
					"lon": <LONGITUDE>
				},
	"friends": [<LISTA-ID-AMIGOS>],
	"stickers": [
			<STICKER-ID>: <STICKER-RELEVANCE>,
			...
			] ,
	"ranking": {
					"social": <RANKING-SOCIAL>,
					"buzz": <RANKING-MOVIMENTACAO>,
					"overall": <RANKING-OVERALL>
				}	
}
```

Caso não exista um local com o ID especificado, será retornada uma resposta HTTP com código 404 (NOT FOUND).

#### Buscar locais

Para buscar locais, deve-se fazer uma requisição GET:
```
GET https://api.stigapp.co/places[?page=<PAGE-NO>&q=<QUERY-STRING>]
```

Em caso de sucesso, o servidor retornará uma resposta HTTP com código 200 (OK) retornando um JSON no seguinte formato:

```
{
	"results": [
					{
						"id": <ID-LOCAL>,
						"name": <NOME-DO-LOCAL>,
						"image": <URL-DA-IMAGEM-DO-LOCAL>,
						"description": <DESCRICAO>,
						"location": {
										"lat": <LATITUDE>,
										"lon": <LONGITUDE>
									},
						"friends": [<LISTA-ID-AMIGOS>],
						"stickers": {
								<STICKER-ID>: <STICKER-RELEVANCE>,
								...
								} ,
						"ranking": {
										"social": <RANKING-SOCIAL>,
										"buzz": <RANKING-MOVIMENTACAO>,
										"overall": <RANKING-OVERALL>
									}	
					},
					...
				],
	"count": <TOTAL-LOCAIS>,
	"next": <LINK-PROX-PAGINA>,
	"previous": <LINK-ANT-PAGINA>,
}
```

Os locais deverão ser ordenados em ordem crescente de distância em relação ao usuário.

Os campos "prev" e "next" aparecerão se necessário.

Caso não existam locais na página especificada, será retornada uma resposta HTTP com código 404 (NOT FOUND).

### Comentários

#### Ver comentário

Todo comentário está associados à um local. Cada comentário também possui um identificador associado ao local. Para acessar um comentário, deve-se fazer uma requisição GET:

```
GET https://api.stigapp.co/places/<ID-LOCAL>/comments/<ID-COMENTARIO>
```

Em caso de sucesso, o servidor retornará uma resposta HTTP com código 200 (OK) retornando um JSON no seguinte formato:

```
{
	"id": <ID-COMENTARIO>,
	"place": <ID-LOCAL>,
	"user": <ID-USUARIO>,
	"content": <TEXTO-COMENTARIO>,
	"stickers": <LISTA-ID-STICKERS-CODIFICADA>,
	"timestamp": <TIMESTAMP-DA-MENSAGEM>,
	"parent": <ID-MENSAGEM-REPLY>
}
```

Caso o local especificado não exista, ou caso o comentário não exista, será retornada uma resposta HTTP com código 404 (NOT FOUND).

#### Ver comentários sobre um local

Para acessar os comentários associados à um local, deve-se fazer uma requisição GET:
```
GET https://api.stigapp.co/places/<ID-LOCAL>/comments[?page=<PAGE-NO>&filter=<LISTA-ID-STICKERS>]
```

Em caso de sucesso, o servidor retornará uma resposta HTTP com código 200 (OK) retornando um JSON no seguinte formato:

```
{
	"results": [
					{
						"id": <ID-COMENTARIO>,
						"user": <ID-USUARIO>,
						"place": <ID-LOCAL>,
						"text": <TEXTO-COMENTARIO>,
						"stickers": <LISTA-ID-STICKERS-CODIFICADA>,
						"timestamp": <TIMESTAMP-DA-MENSAGEM>
					},
					...
				],
	"count": <TOTAL-COMENTARIOS>,
	"next": <LINK-PROX-PAGINA>,
	"previous": <LINK-ANT-PAGINA>,
}
```

Os comentários deverão ser ordenados em ordem decrescente do timestamp.

Os campos "prev" e "next" aparecerão se necessário.

Caso o local especificado não exista, ou caso não exista comentários na página especificada, será retornada uma resposta HTTP com código 404 (NOT FOUND).

#### Ver replies de um comentário

Para acessar os replies de um comentário, deve-se fazer uma requisição GET:
```
GET https://api.stigapp.co/places/<ID-LOCAL>/comments/reply[?page=<PAGE-NO>&filter=<LISTA-ID-STICKERS>]
```

Em caso de sucesso, o servidor retornará uma resposta HTTP com código 200 (OK) retornando um JSON no seguinte formato:

```
{
	"results": [
					{
						"id": <ID-COMENTARIO>,
						"user_id": <ID-USUARIO>,
						"place_id": <ID-LOCAL>,
						"text": <TEXTO-COMENTARIO>,
						"stickers": <LISTA-ID-STICKERS>,
						"timestamp": <TIMESTAMP-DA-MENSAGEM>
					},
					...
				],
	"count": <TOTAL-COMENTARIOS>,
	"next": <LINK-PROX-PAGINA>,
	"previous": <LINK-ANT-PAGINA>,
}
```

Os comentários deverão ser ordenados em ordem decrescente do timestamp.

Os campos "prev" e "next" aparecerão se necessário.

Caso o local especificado não exista, caso o comentário não exista, ou caso não exista comentários na página especificada, será retornada uma resposta HTTP com código 404 (NOT FOUND).

### Usuários

#### Ver usuário

A cada usuário está associado um campo identificador. Para acessar um usuário, deve-se fazer uma requisição GET:
```
GET https://api.stigapp.co/users/<ID-USER>
```

Em caso de sucesso, o servidor retornará uma resposta HTTP com código 200 (OK) retornando um JSON no seguinte formato:

```
{
	"id": <ID-USER>,
	"name": <NOME-DO-USUÁRIO>,
	"img": <URL-DA-IMAGEM-DO-USUÁRIO>,
	"location": {
					"lat": <LATITUDE>,
					"lon": <LONGITUDE>
				},
	"place": <PLACE-ID>	
}
```

Caso não exista um usuário com o ID especificado, será retornada uma resposta HTTP com código 404 (NOT FOUND). Se o usuário não for amigo do usuário especificado, será retornada uma resposta HTTP com código 403 (UNAUTHORIZED).

#### Ver histório de check-in de um usuário

Para acessar o histório de check-in de um usuário, deve-se fazer uma requisição GET:
```
GET https://api.stigapp.co/users/<ID-USER>/checkin[?page=<PAGE-NO>]
```

Em caso de sucesso, o servidor retornará uma resposta HTTP com código 200 (OK) retornando um JSON no seguinte formato:

```
{
	"result":	[
					{
						"id": <ID-LOCAL>,
						"timestamp": <TIMESTAMP-DO-CHECK-IN>
					},
					...
				],
	"count": <TOTAL-LOCAIS>,
	"next": <LINK-PROX-PAGINA>,
	"previous": <LINK-ANT-PAGINA>,
}
```

Os locais deverão ser ordenados em ordem decrescente do timestamp.

Os campos "prev" e "next" aparecerão se necessário.

Caso o usuário especificado não exista, ou caso não existam locais na página especificada, será retornada uma resposta HTTP com código 404 (NOT FOUND). Caso o usuário especificado não seja amigo do usuário-cliente, será retornada uma resposta HTTP com código 403 (UNAUTHORIZED).


Criando recursos
----------------

### Locais

Para criar um novo local, deve-se fazer uma requisição POST:

```
POST https://api.stigapp.co/places

{
	"name": <NOME-DO-LOCAL>,
	"img": <URL-DA-IMAGEM-DO-LOCAL>,
	"description": <DESCRICAO>
	"location": {
					"lat": <LATITUDE>,
					"lon": <LONGITUDE>
				}
}
```

Em caso de sucesso, será retornada uma resposta HTTP 201 (CREATED) com o seguinte JSON:
```
{
  "id": <ID-LOCAL>,
  "name": <NOME-DO-LOCAL>,
	"img": <URL-DA-IMAGEM-DO-LOCAL>,
	"description": <DESCRICAO>,
	"location": {
					"lat": <LATITUDE>,
					"lon": <LONGITUDE>
				},
	"friends": [<LISTA-ID-AMIGOS>],
	"stickers": {
			<STICKER-ID>: <STICKER-RELEVANCE>,
			...
			} ,
	"ranking": {
					"social": <RANKING-SOCIAL>,
					"buzz": <RANKING-MOVIMENTACAO>,
					"overall": <RANKING-OVERALL>
				}	
}
```

Caso o usuário não tenha as permissões adequadas, será retornada uma resposta HTTP com código 403 (UNAUTHORIZED).

#### Fazer check-in

Para fazer check-in em um local, deve-se fazer uma requisição POST:

```
POST https://api.stigapp.co/places/<PLACE-ID>/checkin
```
Em caso de sucesso, será retornada uma resposta HTTP 201 (CREATED). Caso o local não exista, será retornada uma resposta HTTP com código 404 (NOT FOUND).

### Usuários

Para cadastrar um novo usuário, deve-se fazer uma requisição POST (não há a necessidade de autenticação nessa requisição):

```
POST https://api.stigapp.co/users

{
	"fb-id": <USER-ID-USUARIO>,
	"fb-access-token": <USER-ACCESS-TOKEN>
}
```

O usuário será criado apenas se os campos forem compatíveis. Não devem existir dois usuários com o mesmo fb-id.

Em caso de sucesso, será retornada uma resposta HTTP 201 (CREATED). Caso o usuário não tenha as permissões adequadas, será retornada uma resposta HTTP com código 403 (UNAUTHORIZED). Caso o usuário já exista, será retornada uma resposta HTTP com código 409 (CONFLICT).

### Comentários

#### Adicionar comentário à local
Para adicionar um comentário à um local, deve-se fazer uma requisição POST:
```
POST https://api.stigapp.co/places/<PLACE-ID>/comments

{
	"text": <TEXTO-COMENTARIO>,
	"stickers": <LISTA-ID-STICKERS>
}
```

Em caso de sucesso, será retornada uma resposta HTTP 201 (CREATED). com o seguinte JSON:
```
{
	"id": <ID-COMENTARIO>,
	"place_id": <ID-LOCAL>,
	"user_id": <ID-USUARIO>,
	"text": <TEXTO-COMENTARIO>,
	"stickers": <LISTA-ID-STICKERS>,
	"timestamp": <TIMESTAMP-DA-MENSAGEM>,
	"reply": null
}
```
Caso o usuário não tenha as permissões adequadas, será retornada uma resposta HTTP com código 403 (UNAUTHORIZED). Caso o local não exista, será retornada uma mensagem HTTP com código 404 (NOT FOUND).

#### Adicionar reply à um comentário

Para adicionar um reply à um comentário, deve-se fazer uma requisição POST:
```
POST https://api.stigapp.co/places/<PLACE-ID>/comments/<COMMENT-ID>/reply

{
	"text": <TEXTO-COMENTARIO>,
	"stickers": <LISTA-ID-STICKERS>
}
```

Em caso de sucesso, será retornada uma resposta HTTP 201 (CREATED) com o seguinte JSON:
```
{
	"id": <ID-COMENTARIO>,
	"place_id": <ID-LOCAL>,
	"user_id": <ID-USUARIO>,
	"text": <TEXTO-COMENTARIO>,
	"stickers": <LISTA-ID-STICKERS>,
	"timestamp": <TIMESTAMP-DA-MENSAGEM>,
	"reply": <ID-MENSAGEM-REPLY>
}
```
Caso o usuário não tenha as permissões adequadas, será retornada uma resposta HTTP com código 403 (UNAUTHORIZED). Caso o local não exista, ou o comentário não exista, será retornada uma mensagem HTTP com código 404 (NOT FOUND).
 
Dúvidas? Sugestões?
========

Entre em contato de qualquer maneira, pelamor
