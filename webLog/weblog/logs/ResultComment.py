# a list of comment strings
class ResultComment:
        
    #constructeur
    def __init__(self,comment=""):
        if(not isinstance(comment,basestring)):
            raise "Error : trying to add an object which is not of the 'basestring' type"
        
        if(comment==""):
            self.commentList = []
        else:
            self.commentList = [comment]

    #ajoute un commentaire
    def addComment(self,comment):
        if(not isinstance(comment,basestring)):
            raise "Error : trying to add an object which is not of the 'basestring' type"
        self.commentList.append(comment)
    
    # renvoie l'ensemble des commentaires sous forme de chaine
    def getAllCommentsAsAString(self):
        commentString = ""
        for comment in self.commentList:
            commentString += comment+"\n"
        return commentString
    
    # renvoie la liste de commentaires (liste de strings)
    def getCommentList(self):
        return self.commentList
    
    #la liste de commentaires est-elle vide ?
    def isEmpty(self):
        return (len(self.commentList)==0)
    
    #operateur d'addition
    def __add__(self,testResultComment):
        if(not isinstance(testResultComment,ResultComment)):
           raise "Error : trying to add an object which is not of the 'ResultComment' type"
        
        _testResultComment = self        
        for comment in testResultComment.getCommentList():
            _testResultComment.addComment(comment)
        return _testResultComment
