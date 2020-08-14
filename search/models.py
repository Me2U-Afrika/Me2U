from django.db import models
# from django.contrib.auth.models import User
from users.models import User


# Create your models here.
class SearchTerm(models.Model):
    q = models.CharField(max_length=50)
    search_date = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField()
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    tracking_id = models.CharField(max_length=70, default='')

    class Meta:
        ordering = ['-search_date']

    def __unicode__(self):
        return self.q

#
# class SearchEngine(models.Model):
#
#     def createindextables(self):
#         self.con.execute('create table wordlist(word)')
#         self.con.execute('create table wordlocation(urlid,wordid,location)')
#         self.con.execute('create table link(fromid integer,toid integer)')
#         self.con.execute('create table linkwords(wordid,linkid)')
#         self.con.execute('create table urllist(url)')
#         self.con.execute('create index wordidx on wordlist(word)')
#         self.con.execute('create index urlidx on urllist(url)')
#         self.con.execute('create index wordurlidx on wordlocation(wordid)')
#         self.con.execute('create index urltoidx on link(toid)')
#         self.con.execute('create index urlfromidx on link(fromid)')
#         self.dbcommit()
