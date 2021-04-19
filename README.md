# Como correr

Para correr basta executar o script [(run_local)](run_local.sh)
  
    $ ./run_local.sh
Este script irá lançar a API em: http://localhost:5000/

 [Login.py](login.py) é uma ficheiro que permite registar novos utilizadores e fazer o login.
  
    $ python3 login.py


# Sobre a implementação

Antes de falamos sobre a implementação, é importante referir que dependendo da tipologia da API esta pode ser mais ou menos rígida no que diz respeito à autenticação dos seus utilizadores, para isso devemos ter em conta os requisitos do cliente. Uma vez que a lista de requisitos não era muito extensa foram tomas alguma decisões referentes ao comportamento do login, sendo estas explicadas posteriormente.

A API foi desenvolvida em python na framework Flask. Esta é constituída por 3 routes sendo elas `register`, `login`, `home`.

A API também conta com uma base de dados mysql onde foram inseridos os utilizadores.

Após a análise de vários algoritmos de rate limit entre os quais, fixed window, moving window, Token Bucket, Hard stop, Soft Stop, Throttled Stop e Billable Stop, decidi implementar uma versão diferente.

Na minha implementação é permitido ao utilizador falhar a autenticação 2 vezes sem qualquer tipo de repercussão, aparecendo apenas um aviso que este terá mais uma tentativa. No caso de este falhar uma 3 vez o seu IP ficará bloqueado por um período de 30 minutos. Após estes terão mais três tentativas.


No caso de o utilizador falhar x < 3 e não efetuar o login estas x falhas serão tidas em conta durante um período de 30 minutos após o qual serão descartadas.


Se o utilizador falhar x < 3 e efetuar o login de forma correta estas x falhas serão descartadas. Esta condição poderá ser considerada um falha visto que se o atacante souber os dados de uma conta (username e password) poderá tentar fazer bruteforce cometendo duas falhas e um login correto diversas vezes.
Para mitigar esta condição coloquei um limite de 100 pedidos por dia, 30 pedidos por hora e no máximo um 1 pedido a cada 2 segundos, desta forma não irá afetar o utilizador mas será uma taxa impraticável para bruteforce. Após ultrapassar este limite será retornado erro o 429.


Esta implementação também têm em consideração o caso de vários IP's tentarem fazer login numa conta. Para termos essa informação foi criado um dicionário onde a chave era o username e os valores uma lista de timestamps, correspondendo estes a uma tentativa incorreta de login para esse utilizador.


No caso mais extremo que é quando o utilizador inicia sessão a cada duas tentativas erradas, se existirem mais de 20 tentativas erradas para o mesmo username sabemos que foram feitas por pelo menos dois IP's visto que cada utilizador pode fazer 30 pedidos por hora, neste caso 10 certos e 20 errados. Também é possível perceber que existe tentativas de início de sessão por parte de diferentes Ip's se a diferença entre dois timestamps for inferior a 2 segundos visto que cada utilizador só pode fazer um pedido a cada 2 segundos.
Após percebermos que existiu tentativas por mais do que um IP a conta fica bloqueada.


De forma a desbloquear a conta seria enviado um email de recuperação no entanto esta funcionalidade não foi implementada uma vez que não estava no âmbito do desafio.

No caso de não queremos bloquear um IP poderíamos implementar uma API Key, ficando a mesma bloqueada caso não fossem cumpridas as regras estabelecidas.


Se fosse necessário um controlo mais restrito, poderia ser implementado uma whitelist de IP's.

Para terminar esta não era a unica forma de implementar um rate limit de autenticação no entanto é uma implementação válida (um pouco restritiva :) ).
Caso seja necessário terei todo o gosto em fazer as alterações propostas.
