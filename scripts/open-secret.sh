mkdir -p secrets_
cp secrets/$1 secrets_/$1
ansible-vault decrypt secrets_/$1 --vault-password-file .vault_pass.txt