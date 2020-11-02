from django.db import models
# from django.contrib.auth.models import User
from users.models import User


# Create your models here.
class SearchTerm(models.Model):
    q = models.CharField(max_length=50)
    search_date = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField()
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    category_searched = models.CharField(max_length=150, blank=True, null=True, default='All categories')
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

# class Wordlist(models.Model):
#     word = models.CharField(max_length=50)
#
#
# class Urllist(models.Model):
#     url = models.CharField()
#
#
# class Wordlocation(models.Model):
#     wordid = models.ForeignKey(Wordlist, on_delete=models.CASCADE)
#     urlid = models.ForeignKey(Urllist, on_delete=models.CASCADE)
#     location = models.CharField()
#
#
# class Link(models.Model):
#     fromid = models.IntegerField()
#     toid = models.IntegerField()
#
#
# class Linkwords(models.Model):
#     wordid = models.ForeignKey(Wordlist, on_delete=models.CASCADE)
#     linkid = models.ForeignKey(Link, on_delete=models.CASCADE)
