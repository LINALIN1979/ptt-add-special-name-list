# ptt-add-special-name-list
Extract Ptt users list from article and add to special name list

### Prerequisite
- python 2.7

### How to use
1. On Ptt, send the article to your email box
2. On Ptt, clean up all your special name list 
3. Go to your email box and store the article to file (e.g. article.txt)
4. Use below command to extract users list from article and add to your 

```
./main.py -i article.txt -u <your_ptt_id> -p <ptt_password>
```

