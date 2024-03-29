from django.shortcuts import render, redirect
from .models import *
from django.contrib import messages
import bcrypt
from django.http import JsonResponse #imported in order to display django errors via ajax
from django.core.files.storage import FileSystemStorage #imported in order to display uploaded images
from django.urls import reverse #imported in order to pass variables when redirecting
from django.db.models import Q #imported in order to filter multiple queries at once
# import operator #imported in order to eliminate spaces in the search bar
# from django.db.models.functions import Lower, Replace
import json
# from tkinter import* #imported in order to use dialog boxes
# from tkinter import messagebox #imported to use messages on dialog boxes


def regAndLoginPage(request):
    return render(request, "regAndLogin.html")

def processRegistration(request):
    print("THIS FUNCTION PROCESSES THE FORM FOR REGISTERING AN ACCOUNT.")
    print("This is the data submitted on the form via ajax/jquery.")
    print(request.POST.get)
    print("This is the data submitted on the form.")
    print("*"*50)
    print(request.POST)
    print("*"*50)
    registrationErrors = User.objects.registrationValidator(request.POST)
    # print("These are the errors submitted on the registration form.")
    # print(registrationErrors)
    if len(registrationErrors) > 0:
        for key, value in registrationErrors.items():
            messages.error(request,value)
        #When an error occurs on one field input, the below code keeps the fields that are filled out correctly instead of removing all inputs.
            request.session['rememberFirstName'] = request.POST['userFirstName']
            request.session['rememberLastName'] = request.POST['userLastName']
            request.session['rememberEmail'] = request.POST['initialEmail']
            request.session['rememberBirthdayMonth'] = request.POST.get('birthdayMonth', False)
            request.session['rememberBirthdayDay'] = request.POST.get('birthdayDay', False)
            request.session['rememberBirthdayYear'] = request.POST.get('birthdayYear', False)
        return JsonResponse({"errors": registrationErrors}, status=400)
    else:
        hashedPassword = bcrypt.hashpw(request.POST['initialPassword'].encode(), bcrypt.gensalt()).decode()
        print("This is the birthday month:", request.POST.get('birthdayMonth'))
        newUser = User.objects.create(firstName = request.POST['userFirstName'].capitalize(), lastName = request.POST['userLastName'].capitalize(), emailAddress = request.POST['initialEmail'], birthdayMonth = request.POST.get('birthdayMonth'), birthdayDay = request.POST.get('birthdayDay'), birthdayYear = request.POST.get('birthdayYear'), password = hashedPassword, confirmPassword = hashedPassword)
        request.session['loginInfo'] = newUser.id
    print("THIS IS THE LAST PRINT STATEMENT IN THE THE PROCESS REGISTRATION ROUTE.")
    return redirect("/wall")

def processLogin(request):
    print("THIS FUNCTION PROCESSES THE FORM FOR LOGGING IN.")
    # print("*"*50)
    loginErrors = User.objects.loginValidator(request.POST)
    # print(loginErrors)
    if len(loginErrors) > 0:
        for key, value in loginErrors.items():
            messages.error(request,value, extra_tags="loginErrors") #Extra tags separates the two types of validation errors (login and registration)
            request.session['rememberEmail'] = request.POST['userEmail'] #When an error occurs on one field input, the below code keeps the fields that are filled out correctly instead of removing all inputs.
        return redirect('/')
    else:
        loginUser = User.objects.filter(emailAddress= request.POST['userEmail'])[0] #if no errors hit and the user did successfully register, this filters to get that correctly submitted email and password
        request.session['loginInfo'] = loginUser.id #now store that info in session into a new variable
        print("THIS IS THE LAST PRINT STATEMENT IN THE THE PROCESS LOGIN ROUTE.")
    return redirect("/wall")

def wall(request):
    print("THIS FUNCTION IS THE WALL OF THE COLLEGEBOOK")
    loggedInUser = User.objects.get(id=request.session['loginInfo'])
    #make the loggedinuser friends with themselves so their posts display on the wall (if friends statement)
    loggedInUser.friends.add(loggedInUser)
    loggedInUsersFriends = loggedInUser.friends.all()
    # print("These are the logged in user's friends:", loggedInUsersFriends)
    wallOfLoggedInUser = Message.objects.filter(userReceivesPost = loggedInUser).order_by('-createdAt')
    allMessages = Message.objects.all().order_by('-createdAt')
    # print("These are the messages on the logged in user's wall:", allMessages)
    # print("These are all the users the logged in user sent friend requests to:", loggedInUser.friends.all())
    notifications = Notification.objects.filter(user=loggedInUser)
    # print("These are the logged in user's notifications:", notifications)
    print("THIS IS THE LAST PRINT STATEMENT IN THE WALL FUNCTION")
    context = {
        'loggedInUser': loggedInUser,
        'allMessages': allMessages,
        'wallOfLoggedInUser': wallOfLoggedInUser,
        'notifications': Notification.objects.all,
        'loggedInUsersFriends': loggedInUsersFriends,
        'loggedInUsersNotifs': Notification.objects.filter(user=loggedInUser)
    }
    return render(request, "wall.html", context)

#The above line of code is for the registration and login.

def loggedInUsersPage(request, messageId=0):
#if they are not logged in (if loginInfo is not in session), then this directs the user back to the index page
    if 'loginInfo' not in request.session:
        return redirect('/')
    print("THIS IS THE LOGGED IN USERS PAGE ROUTE.")
    # print("This prints the currently logged in user.")
    loggedInUser = User.objects.get(id=request.session['loginInfo'])
    # print(loggedInUser)
    if loggedInUser.notifications < 0:
        # print("The notification counter is negative and needs to be reset to 0.")
        resetNotificationCounter = User.objects.filter(id=request.session['loginInfo']).update(notifications=0) 
    # if not loggedInUser.notifications:
    #     resetNotificationCounter = User.objects.filter(id=request.session['loginInfo']).update(notifications=0) 
    # print("This prints all the messages posted on the wall (by the user and by others) of the logged in user and orders them from latest post created.")
    wallOfLoggedInUser = Message.objects.filter(userReceivesPost = loggedInUser).order_by('-createdAt')
    # print(wallOfLoggedInUser)
    loggedInUsersNotifs = Notification.objects.filter(user=loggedInUser)
    # print("This prints the notifications of the logged in user:", loggedInUsersNotifs)
    # print("Comment notifs:", loggedInUsersNotifs.commenter)
    # how to do a multi query #wallOfLoggedInUser = Message.objects.filter(Q(user = (loggedInUser)) | Q(userReceivesPost = (loggedInUser))).order_by('-createdAt')
    if messageId: #if these lines of code run it means a like occurred
        # print("This prints the id of the message that was just liked and passed via params from the userLikes function.")
        messageId = messageId
        # print(messageId)
        # print("This prints the message object.")
        messageBeingLiked = Message.objects.get(id=messageId)
        # print(messageBeingLiked)
        # print("This prints the amount of likes the message has.")
        # print(messageBeingLiked.likeMessageCount)
        if messageBeingLiked.likeMessageCount > 3:
                likesCountMinusDisplayNames = (messageBeingLiked.likeMessageCount) - 2
                # print("This is the like count minus the display names:", likesCountMinusDisplayNames)
                displayCount = Message.objects.filter(id=messageId).update(likeMessageCountMinusDisplayNames=likesCountMinusDisplayNames) 
    # print("This prints all the users that have an account except the logged in user.")
    allUsers = User.objects.exclude(id=request.session['loginInfo']).order_by('?') #filter will be randomized
    # print(allUsers)
    friends = loggedInUser.friends.all().order_by('?').exclude(id = loggedInUser.id)
    print("These are all the friends of the logged in user:", friends)
    friendCount = friends.count() 
    # print("This is the friend count:", friendCount)
    # print("This is the notification count", Notification.objects.filter(user=loggedInUser).count())
    loggedInUsersNotifs = Notification.objects.filter(user=loggedInUser)
    print("These are the notifications:", loggedInUsersNotifs)
    print("*"*50)
    context = {
        'loggedInUser': User.objects.get(id=request.session['loginInfo']),
        'wallOfLoggedInUser': wallOfLoggedInUser,
        'allUsers': allUsers,
        'friends': friends,
        'friendCount': friendCount,
        'notifications': Notification.objects.all,
        'loggedInUsersNotifs': Notification.objects.filter(user=loggedInUser)
    }
    return render(request, "loggedInUsersPage.html", context)

def processProfilePic(request):
    print("*"*50)
    print("THIS FUNCTION PROCESSES THE FORM/UPLOADING OF A PROFILE PICTURE.")
    # if request.is_ajax():
    #     if request.method == 'POST':
    #         print("POST request occurred.")
    if request.method == 'POST' and request.FILES.get('userProfilePic'):
        userProfilePic = request.FILES['userProfilePic']
        print("This is the submitted profile picture:", userProfilePic)
#The below code is how to upload a file in django development stage
        # fileSystem = FileSystemStorage()
        # uploadedImage = fileSystem.save(userProfilePic.name, userProfilePic)
        # uploadedImageURL = fileSystem.url(uploadedImage)
        # print("This is the uploaded image url:", uploadedImageURL)
        # addProfilePic = User.objects.filter(id=request.session['loginInfo']).update(profilePic=uploadedImageURL)
#The above code is how to upload a file in django development stage
        loggedInUser = User.objects.get(id = request.session['loginInfo'])
        loggedInUser.profilePic = userProfilePic
        print("This is the image being saved in the user object:", loggedInUser, loggedInUser.profilePic)
        loggedInUser.save()
        # uploadToCloudinary = cloudinary.uploader.upload(request.FILES['userProfilePic'])
        # print("This is what is being uploaded to cloudinary:", uploadToCloudinary)
    print("THIS IS THE LAST PRINT STATEMENT IN THE PROCESS PROFILE PIC ROUTE.")
    print("*"*50)
    return redirect("/home")

def userDeletesProfilePic(request):
    print("THIS FUNCTION REMOVES THE PROFILE PIC OF THE USER FROM THE USER FROM THE DATABASE.")
    # deleteProfilePic = User.objects.filter(id=request.session['loginInfo']).update(profilePic="")
#The below code is the same as the update line, but this works with cloudinary and the other does not 
    loggedInUser = User.objects.get(id = request.session['loginInfo'])
    loggedInUser.profilePic = ""
    print("This is the image being deleted in the user object:", loggedInUser, loggedInUser.profilePic)
    loggedInUser.save()
#The below code is the same as the update line, but this works with cloudinary and the other does not 
    print("THIS IS THE LAST PRINT STATEMENT IN THE USER DELETES PROFILE PIC ROUTE.")
    return redirect("/home")

def processProfileHeader(request):
    print("THIS FUNCTION PROCESSES THE FORM FOR UPLOADING THE PROFILE HEADER THAT IS UNDERNEATH THE PROFILE PHOTO.")
    # print("*"*50)
    # print(request.POST)
    submittedProfileHeader = request.POST['userProfileHeader']
    # print(submittedProfileHeader)
    # print("*"*50)
    addProfileHeader= User.objects.filter(id=request.session['loginInfo']).update(profileHeader=submittedProfileHeader) 
    print("THIS IS THE LAST PRINT STATEMENT IN THE PROCESS PROFILE HEADER ROUTE.")    
    return redirect("/home")

def processProfileIntro(request):
    print("THIS FUNCTION PROCESSES THE FORM FOR UPLOADING A PROFILE INTRODUCTION.")
    print("*"*50)
    profileIntroErrors = User.objects.profileIntroValidator(request.POST)
    if request.POST['userCheckBox'] == 'true':
        request.session['rememberUniversity'] = request.POST['userUniversity']
        request.session['rememberHighSchool'] = request.POST['userHighSchool']
        request.session['rememberDormBuilding'] = request.POST['userDormBuilding']
        request.session['rememberHomeTown'] = request.POST['userHomeTown']
        print("This print statement means the checkbox is checked.", request.POST['userCheckBox'])
        submittedUserUniversity = request.POST['userUniversity']
        # print("This is the university the user submitted:", submittedUserUniversity)
        submittedUserHighSchool = request.POST['userHighSchool']
        # print("This is the highschool the user submitted:", submittedUserHighSchool)
        submittedUserDormBuilding = request.POST['userDormBuilding']
        # print("This is the dorm building the user submitted:", submittedUserDormBuilding)
        submittedUserHomeTown= request.POST['userHomeTown']
        # print("This is the home town the user submitted:", submittedUserHomeTown)
        print("This will save the data if the user chooses to input it, but still also means the user chooses to hide it.")
        addProfileIntro = User.objects.filter(id=request.session['loginInfo']).update(userUniversity=submittedUserUniversity, userHighSchool = submittedUserHighSchool, userDormBuilding = submittedUserDormBuilding, userHomeTown = submittedUserHomeTown, userCheckBox = True ) 
        print("*"*50)
        print("THIS IS THE LAST PRINT STATEMENT IN THE PROCESS PROFILE INTRO ROUTE.")   
    elif request.POST['userCheckBox'] == 'false':
        if len(profileIntroErrors) > 0:
            for key, value in profileIntroErrors.items():
                messages.error(request,value)
            #When an error occurs on one field input, the below code keeps the fields that are filled out correctly instead of removing all inputs.
                request.session['rememberUniversity'] = request.POST['userUniversity']
                request.session['rememberHighSchool'] = request.POST['userHighSchool']
                request.session['rememberDormBuilding'] = request.POST['userDormBuilding']
                request.session['rememberHomeTown'] = request.POST['userHomeTown']
                # print("These are the errors submitted on the profile intro form.")
            return JsonResponse({"errors": profileIntroErrors}, status=400)
        else:
            print("This will save the data if the user chooses to input it, but still also means the user chooses to hide it.")
            submittedUserUniversity = request.POST['userUniversity']
            # print("This is the university the user submitted:", submittedUserUniversity)
            submittedUserHighSchool = request.POST['userHighSchool']
            # print("This is the highschool the user submitted:", submittedUserHighSchool)
            submittedUserDormBuilding = request.POST['userDormBuilding']
            # print("This is the dorm building the user submitted:", submittedUserDormBuilding)
            submittedUserHomeTown= request.POST['userHomeTown']
            # print("This is the home town the user submitted:", submittedUserHomeTown)
            request.session['rememberUniversity'] = request.POST['userUniversity']
            request.session['rememberHighSchool'] = request.POST['userHighSchool']
            request.session['rememberDormBuilding'] = request.POST['userDormBuilding']
            request.session['rememberHomeTown'] = request.POST['userHomeTown']
            addProfileIntro = User.objects.filter(id=request.session['loginInfo']).update(userUniversity=submittedUserUniversity, userHighSchool = submittedUserHighSchool, userDormBuilding = submittedUserDormBuilding, userHomeTown = submittedUserHomeTown, userCheckBox = False ) 
            print("*"*50)
            print("THIS IS THE LAST PRINT STATEMENT IN THE PROCESS PROFILE INTRO ROUTE.")    
    return redirect("/home")

def processMessage(request, userFirstName, userLastName, userId):
    print("*"*50)
    print("THIS FUNCTION PROCESSES THE FORM OF POSTING A MESSAGE.")
    postAMessageErrors = Message.objects.messageValidator(request.POST) #linking the messageValidator instance in the model that's containing the errors
    # print(postAMessageErrors)
    if len(postAMessageErrors) > 0:
        for key, value in postAMessageErrors.items():
            messages.error(request,value)
        return JsonResponse({"errors": postAMessageErrors}, status=400)
    else:
        print("This prints the messaged created by the logged in user.")
        userMessage = request.POST['userMessage']
        print(userMessage)
        areFriends = request.POST['areFriends']
        print("This prints the are Friends boolean:", areFriends )
        print("This prints the logged in user.")
        loggedInUser = User.objects.get(id=request.session['loginInfo'])
        print(loggedInUser)
        recipientOfPost = request.POST['userWhoReceivesPost'] # is a number but as a string so need to convert before comparison   
        print("The id of the user receiving the post:", recipientOfPost)
        recipientOfPostObject = User.objects.get(id = recipientOfPost)
        # print("These are the friends of the user receiving the posts:", recipientOfPostObject.friends.all())
        if loggedInUser.id == int(recipientOfPost): #this means the logged in user is writing on their own wall
            #this creates the message and saves it to the database
            submittedMessageByUser = Message.objects.create(message = userMessage, user = loggedInUser, userReceivesPost_id = recipientOfPost)
            userReceivesNewPost = User.objects.get(id = recipientOfPost)
            notifyUser = Notification.objects.create(user = userReceivesNewPost, message = submittedMessageByUser) #This creates a notification for the user receiving the posted message
            print("THIS IS THE LAST PRINT STATEMENT IN THE PROCESS POSTING A MESSAGE ROUTE.")    
            return redirect("/home")
        else: #this means the logged in user is writing a post to a different user
            if recipientOfPostObject in loggedInUser.friends.all() and loggedInUser in recipientOfPostObject.friends.all():
                print("This means they are friends.")
                submittedMessageByUser = Message.objects.create(message = userMessage, user = loggedInUser, userReceivesPost_id = recipientOfPost) #this creates the message and saves it to the database
                messageObject = Message.objects.get(id=submittedMessageByUser.id) #This can be retrieved now because the code line above created the message instance
                print("This is the message object:", messageObject)
                confirmFriendshipOfRecipientOfPost = Message.objects.filter(id=messageObject.id).update(arefriends=True)
                print("This is the message field updated to true to confirm the friendship:", confirmFriendshipOfRecipientOfPost)
                userReceivesNewPost = User.objects.get(id = recipientOfPost)
                notifyUser = Notification.objects.create(user = userReceivesNewPost, message = submittedMessageByUser) #This creates a notification for the user receiving the posted message
                userReceivesNewPost.notifications += 1 #a counter for all the notifications (posted messages, comments, and friend requests)
                userReceivesNewPost.save()
            if recipientOfPostObject not in loggedInUser.friends.all() and loggedInUser not in recipientOfPostObject.friends.all():
                print("You're not friends! Send friend request")
            if recipientOfPostObject not in loggedInUser.friends.all() and loggedInUser in recipientOfPostObject.friends.all():
                print("This means the friend request is still pending/hasn't been accepted or declined yet.")
        print("*"*50)
        print("THIS IS THE LAST PRINT STATEMENT IN THE PROCESS MESSAGE ROUTE.")    
        return redirect(reverse('specificUsersPage', args=(userFirstName, userLastName, userId,))) #using the name of the url to redirect and passing the variables/params to the form rendering the template

def processMessageOnWall(request):
    # print("*"*50)
    print("THIS FUNCTION PROCESSES THE FORM OF POSTING A MESSAGE ON THE WALL.")
    postAMessageErrors = Message.objects.messageValidator(request.POST) #linking the messageValidator instance in the model that's containing the errors
    # print(postAMessageErrors)
    if len(postAMessageErrors) > 0:
        for key, value in postAMessageErrors.items():
            messages.error(request,value)
        return JsonResponse({"errors": postAMessageErrors}, status=400)
    else:
        #print("This prints the messaged created by the logged in user.")
        userMessage = request.POST['userMessage']
        print(userMessage)
        #print("This prints the logged in user.")
        loggedInUser = User.objects.get(id=request.session['loginInfo'])
        # print(loggedInUser)
        recipientOfPost = request.POST['userWhoReceivesPost'] # is a number but as a string so need to convert before comparison   
        print("The id of the user receiving the post:", recipientOfPost)
        recipientOfPostObject = User.objects.get(id = recipientOfPost)
        print("The id of the loggedInUser:", loggedInUser.id)
        print("These are the friends of the user receiving the posts:", recipientOfPostObject.friends.all())
        print("These are the logged in user's friends:", loggedInUser.friends.all())
        submittedMessageByUser = Message.objects.create(message = userMessage, user = loggedInUser, userReceivesPost_id = recipientOfPost)
        userReceivesNewPost = User.objects.get(id = recipientOfPost)
        notifyUser = Notification.objects.create(user = userReceivesNewPost, message = submittedMessageByUser) #This creates a notification for the user receiving the posted message
        print("THIS IS THE LAST PRINT STATEMENT IN THE PROCESS POSTING A MESSAGE ON THE WALL ROUTE.")    
    return redirect("/wall")

def deleteMessage(request, userFirstName, userLastName, userId):
    # print("*"*50)
    print("THIS FUNCTION DELETES A POSTED MESSAGE.")
    loggedInUser = User.objects.get(id=request.session['loginInfo'])
    messageData = json.loads(request.body)
    # print("This is the received message data:", messageData) # it is in a dictionary so we need to loop through to get the values
    for messageID in messageData.values():
        print("This is the message id:", messageID)
        messageToBeDeleted = Message.objects.get(id = messageID)
        print("This is the message being deleted:", messageToBeDeleted)
        print("This is the user who received the post:", messageToBeDeleted.userReceivesPost) #user object
        if loggedInUser == messageToBeDeleted.userReceivesPost: #this means the logged in user is attempting to delete a message on their own wall and should be directed back here
            messageToBeDeleted.delete()
            print("THIS IS THE LAST PRINT STATEMENT IN THE DELETING A MESSAGE ROUTE.")    
            return redirect("/home")
        else: #this means the user is trying to delete a post they created on a specific user's page
            # print("*"*50)
            messageToBeDeleted = Message.objects.get(id = messageID)
            # print("This is the message being deleted:", messageToBeDeleted)
            messageToBeDeleted.delete()
            userId = messageToBeDeleted.userReceivesPost.id
            print("This is the user's first name of the page to be redirected to:", userId)
            userObject = User.objects.get(id = userId)
            userFirstName = userObject.firstName
            userLastName = userObject.lastName
            userId = userObject.id
            print("This is the user's first name, last name, and id of the page to be redirected to:", userFirstName, userLastName, userId)
            print("THIS IS THE LAST PRINT STATEMENT IN THE PROCESS MESSAGE ROUTE.")    
        return redirect(reverse('specificUsersPage', args=(userFirstName, userLastName, userId,))) #using the name of the url to redirect and passing the variables/params to the form rendering the template

def processComment(request, userFirstName, userLastName, userId):
    postACommentErrors = Comment.objects.commentValidator(request.POST)
    print(postACommentErrors)
    if len(postACommentErrors) > 0:
        for key, value in postACommentErrors.items():
            messages.error(request,value)
        return JsonResponse({"errors": postACommentErrors}, status=400)
    else:
        print("THIS FUNCTION PROCESSES THE FORM FOR POSTING A COMMENT.")
        print("*"* 50)
        print("This is the comment left by the logged in user.")
        comment = request.POST['userComment']
        # print("This is the logged in user's comment:", comment)
        print("This is the post id where the comment is made.")
        messageSelectedForComment = request.POST['postLocationForComment']
        # print(messageSelectedForComment)
        print("This is the user that made the comment.")
        loggedInUser = User.objects.get(id=request.session['loginInfo'])
        print(loggedInUser)
        print("This prints the id of the specific user who received the comment.")
        userReceivesComment = request.POST['userReceivesComment']
        print("This is the user receiving the comment:", userReceivesComment)
        recipientOfComment = User.objects.get(id= userReceivesComment)
        #Now that I have the post that receives the comment(messageSelectedForComment), and the user who receives the comment(userReceivesComment), I can use said variables for a query to obtain its' instances.
        #To do that I need to get the message object via id to use for the foreign key/one to many relationship
        theSpecificPost = Message.objects.get(id = messageSelectedForComment)
        if loggedInUser.id == recipientOfComment.id: #This means the user is commenting on their own page and should be directed home
            print("This print statement means the user is commenting on their own page and should be redirected home.")
            commentByUser = Comment.objects.create(comment = comment, message = theSpecificPost, user = loggedInUser, userReceivesComment = recipientOfComment)
            return redirect("/home")
        else: #This means the user is commenting on someone else's page and should be directed their
            commentByUser = Comment.objects.create(comment = comment, message = theSpecificPost, user = loggedInUser, userReceivesComment = recipientOfComment)
            notifyUser = Notification.objects.create(user = recipientOfComment, comment = commentByUser, commenter = loggedInUser)  #This creates a notification for the user receiving the posted message
            print("This is the user that needs to be notified of the comment that was made on their page:", recipientOfComment)
            recipientOfComment.notifications += 1
            recipientOfComment.save()
            # print("*"* 50)
            print("THIS IS THE LAST PRINT STATEMENT IN THE PROCESS COMMENT ROUTE.")  
    return redirect(reverse('specificUsersPage', args=(userFirstName, userLastName, userId,))) #using the name of the url to redirect and passing the variables/params to the form rendering the template

def processCommentOnWall(request):
    postACommentErrors = Comment.objects.commentValidator(request.POST)
    print(postACommentErrors)
    if len(postACommentErrors) > 0:
        for key, value in postACommentErrors.items():
            messages.error(request,value)
        return JsonResponse({"errors": postACommentErrors}, status=400)
    else:
        print("THIS FUNCTION PROCESSES THE FORM FOR POSTING A COMMENT ON THE WALL.")
        # print("*"* 50)
        loggedInUser = User.objects.get(id=request.session['loginInfo'])
        comment = request.POST['userComment']
        print("This is the logged in user's comment:", comment)
        messageSelectedForComment = request.POST['postLocationForComment']
        print("This is the id of the post location where the comment is made.", messageSelectedForComment)
        userReceivesComment = request.POST['userReceivesComment'] #this is the id number
        recipientOfComment = User.objects.get(id= userReceivesComment)
        print("The person recieving the comment:", recipientOfComment)
        #Now that I have the post that receives the comment(messageSelectedForComment), and the user who receives the comment(userReceivesComment), I can use said variables for a query to obtain its' instances.
        #To do that I need to get the message object via id to use for the foreign key/one to many relationship
        theSpecificPost = Message.objects.get(id = messageSelectedForComment)
        print("This is the post message object:", theSpecificPost)
        commentByUser = Comment.objects.create(comment = comment, message = theSpecificPost, user = loggedInUser, userReceivesComment = recipientOfComment)
        print("The user who left the comment:",loggedInUser.firstName)
        notifyUser = Notification.objects.create(user = recipientOfComment, comment = commentByUser, commenter = loggedInUser) #This creates a notification for the user receiving the posted message
        return redirect("/wall")

def deleteComment(request, userFirstName, userLastName, userId):
    # print("*"*50)
    print("THIS FUNCTION DELETES A POSTED COMMENT.")
    loggedInUser = User.objects.get(id=request.session['loginInfo'])
    commentData = json.loads(request.body)
    print("This is the received comment data:", commentData) # it is in a dictionary so we need to loop through to get the values
    for commentID in commentData.values():
        print("This is the comment id:", commentID)
        commentToBeDeleted = Comment.objects.get(id = commentID)
        print("This is the comment being deleted:", commentToBeDeleted)
        print("This is the user who received the comment:", commentToBeDeleted.userReceivesComment) #user object
        if loggedInUser == commentToBeDeleted.userReceivesComment: #this means the logged in user is attempting to delete a comment on their own wall and should be directed back here
            commentToBeDeleted.delete()
            print("THIS IS THE LAST PRINT STATEMENT IN THE DELETING A COMMENT ROUTE.")    
            return redirect("/home")
        else: #this means the post attempted to be deleted is on a specific user's page
            # print("*"*50)
            print("This is the id of the comment needed to be deleted", commentID)
            commentToBeDeleted = Comment.objects.get(id = commentID)
            print("This is the comment being deleted:", commentToBeDeleted)
            commentToBeDeleted.delete()
            userFirstName = commentToBeDeleted.userReceivesComment.firstName
            userLastName = commentToBeDeleted.userReceivesComment.lastName
            userId = commentToBeDeleted.userReceivesComment.id
            print("THIS IS THE LAST PRINT STATEMENT IN THE DELETE A MESSAGE ROUTE.")    
        return redirect(reverse('specificUsersPage', args=(userFirstName, userLastName, userId,))) #using the name of the url to redirect and passing the variables/params to the form rendering the template

def specificUsersPage(request, userFirstName, userLastName, userId, messageId = 0, specificUsersPageId = 0):
    # print("*"*50)
    print("THIS IS THE SPECIFIC USER'S PAGE ROUTE.")
    loggedInUser = User.objects.get(id=request.session['loginInfo'])
    # if not loggedInUser.notifications:  #this resets the notification counter when an empty query set occurs if a user sends and unsends a friend request, posts/deletes a post, etc
    #     resetNotificationCounter = User.objects.filter(id=request.session['loginInfo']).update(notifications=0) 
    print("THIS IS THE message id via url on the specific user's route:", messageId)
    print("THIS IS THE user id via url on the specific user's route:", userId)
    specificUsersPage = User.objects.get(id=userId) #retreiving from the url
    # print("This is the object of the specific user's page:", specificUsersPage)
    # specificUsersFirstName = User.objects.get(firstName=userFirstName) #retreiving from the url
    # specificUsersLastName = User.objects.get(lastName=userLastName) #retreiving from the url
    # print("This prints all the messages posted on a page of a specific user and orders them from latest post created.")
    specificUsersMessages = Message.objects.filter(userReceivesPost = userId).order_by('-createdAt')
    message = "You're not friends yet! You need to be friends first"
    if messageId:
        print("THIS IS THE SPECIFIC USER'S PAGE ROUTE THAT WAS REACHED BY THE LOGGED IN USER LIKING A MESAGE ON THE SPECIFIC USER'S PAGE.")
        # print("*"*50)
        # print("This prints the id of the message that was just liked and passed via params from the userLikes function.")
        messageId = messageId
        # print(messageId)
        # print("This prints the message object.")
        messageBeingLiked = Message.objects.get(id=messageId)
        # print(messageBeingLiked)
        print("This prints the amount of likes the message has.")
        print(messageBeingLiked.likeMessageCount)
        if messageBeingLiked.likeMessageCount > 3:
                likesCountMinusDisplayNames = (messageBeingLiked.likeMessageCount) - 3
                print("This is the like count minus the display names:", likesCountMinusDisplayNames)
                displayCount = Message.objects.filter(id=messageId).update(likeMessageCountMinusDisplayNames=likesCountMinusDisplayNames) 
    # print(specificUsersMessages)
    # print("This prints all the users that have an account, excluding the specific user's page")
    allUsers = User.objects.all().exclude(id=specificUsersPage.id).order_by('?')
    # print(allUsers)
    specificUsersFriends = specificUsersPage.friends.all()
    loggedInUserFriends = loggedInUser.friends.all()
    # print("These are the friends of the specific user:", specificUsersFriends)
    # print("These are the friends of the logged in user:", loggedInUserFriends)
    friendCount = (specificUsersPage.friends.count() - int(1)) # subtracting one because the count includes the user themself
    # print("This is the friend count minus one:", friendCount)
    # print("*"*50)
    print("THIS IS THE LAST PRINT STATEMENT OF THE SPECIFIC USER'S PAGE ROUTE.")
    context = {
        'specificUsersPage': specificUsersPage,
        'specificUsersMessages': specificUsersMessages,
        'message' : message,
        'allUsers': allUsers,
        'specificUsersFriends': specificUsersFriends,
        'loggedInUserFriends' : loggedInUserFriends,
        'friendCount': friendCount,
        'loggedInUser': User.objects.get(id=request.session['loginInfo']),
        'notifications': Notification.objects.all,
        'loggedInUsersNotifs': Notification.objects.filter(user=loggedInUser)
    }
    return render(request, "specificUserPage.html", context)

def userLikes(request, userFirstName='firstName', userLastName='lastName', userId=0, messageId = 0, specificUsersPageId = 0): #need to have positional arguments in order to do the reroute to the specific page
    print("THIS IS THE USER LIKES ROUTE")
    print("*"*50)
    print("THIS IS THE MESSAGE ID:", messageId)
    print("THIS IS THE SPECIFICUSERSPAGE ID:", specificUsersPageId)
    print("*"*50)
    print("This is the specific message being liked")
    messageBeingLiked = Message.objects.get(id=messageId)
    print(messageBeingLiked) #prints as a Message Object(#)
    userFirstName = messageBeingLiked.userReceivesPost.firstName # need for params to reroute
    # print(userFirstName)
    userLastName = messageBeingLiked.userReceivesPost.lastName # need for params to reroute
    # print(userLastName)
    userId = messageBeingLiked.userReceivesPost.id # need for params to reroute
    # print(userId)
    # print("This is the user liking the message")
    userWhoLikes = User.objects.get(id=request.session['loginInfo'])
    # print(userWhoLikes) # prints as a User Object(#)
    # print("The id of the users who have liked messages:", messageBeingLiked.userLikes.all())
    print("The id of the user giving the like", userWhoLikes.id)
    print("The id of the user receiving the like", messageBeingLiked.userReceivesPost.id)
    if specificUsersPageId:
        currentPageLocation = User.objects.get(id=specificUsersPageId)
        print("The id of the user whose page is currently being viewed:", currentPageLocation)
    if userWhoLikes in messageBeingLiked.userLikes.all():
        print("You've already liked the message!")
        if userWhoLikes.id != messageBeingLiked.userReceivesPost.id: #if this line of code runs it means the repetitive like attempt occurred on the specific user's page
            return redirect(reverse('specificUsersPage', args=(userFirstName, userLastName, userId, messageId,))) #using the name of the url to redirect and passing the variables/params to the form rendering the template
        else: #if this line of code runs it means the repetitive like attempt occurred on the logged in user's page
            return redirect(reverse('home', args=(messageId,))) #using the name of the url to redirect and passing the variables/params to the form rendering the template
    else:
        if userWhoLikes.id != messageBeingLiked.userReceivesPost.id: #if this line of code runs it means the like occurred on the specific user's page
            print("THIS IS THE LAST PRINT STATEMENT OF THE USER LIKES ROUTE (LIKE IS OCCURING ON A SPECIFIC USER'S PAGE).")
            messageBeingLiked.userLikes.add(userWhoLikes) #This creates the like - userLikes is the instance name in the Message model holding the many to many relationship
            messageBeingLiked.likeMessageCount += 1
            messageBeingLiked.save()
            # return redirect(reverse('specificUsersPage', args=(userFirstName, userLastName, userId, messageId,))) #using the name of the url to redirect and passing the variables/params to the form rendering the template
            return redirect(reverse('specificUsersPage', args=(userFirstName, userLastName, userId, messageId,))) #using the name of the url to redirect and passing the variables/params to the form rendering the template
        else: #if these lines of code run it means the like occurred on logged in user's home page
            messageBeingLiked.userLikes.add(userWhoLikes) #userLikes is the instance name in the Message model holding the many to many relationship
            messageBeingLiked.likeMessageCount += 1
            messageBeingLiked.save()
            print("THIS IS THE LAST PRINT STATEMENT OF THE USER LIKES ROUTE (LIKE IS OCCURRING ON THE LOGGED IN USER'S PAGE).")
        return redirect(reverse('home', args=(messageId,))) #using the name of the url to redirect and passing the variables/params to the form rendering the template
    # return redirect("/home")

def userUnlikes(request, userFirstName='firstName', userLastName='lastName', userId=0, messageId = 0): #need to have positional arguments in order to do the reroute to the specific page
    messageBeingUnliked = Message.objects.get(id=messageId)
    userWhoUnlikes = User.objects.get(id=request.session['loginInfo'])
    userFirstName = messageBeingUnliked.userReceivesPost.firstName # need for params to reroute
    userLastName = messageBeingUnliked.userReceivesPost.lastName # need for params to reroute
    userId = messageBeingUnliked.userReceivesPost.id # need for params to reroute
    if userWhoUnlikes in messageBeingUnliked.userLikes.all(): #this checks if the logged in user has liked the specific message to begin with
        if userWhoUnlikes.id != messageBeingUnliked.userReceivesPost.id: #if this line of code runs it means the 'unliking' occurred on the specific user's page
            messageBeingUnliked.userLikes.remove(userWhoUnlikes) #userLikes is the instance name in the Message model holding the many to many relationship
            messageBeingUnliked = Message.objects.get(id = messageId)
            if messageBeingUnliked.likeMessageCount > 0: #this prevents the subtraction when the user tries to unlike a message they have never liked initially
                print("This is the amount of likes the message has:", messageBeingUnliked.likeMessageCount)
                messageBeingUnliked.likeMessageCount -= 1
                print("This is the amount of likes the message has after subtracting one:", messageBeingUnliked.likeMessageCount)
                messageBeingUnliked.save()
                print("THIS IS THE LAST PRINT STATEMENT OF THE USER UNLIKES ROUTE THAT REDIRECTS TO THE SPECIFIC USER'S PAGE.")
            return redirect(reverse('specificUsersPage', args=(userFirstName, userLastName, userId, messageId,))) #using the name of the url to redirect and passing the variables/params to the form rendering the template
        else: #if these lines of code run it means the 'unliking' occurred on logged in user's home page
            messageBeingUnliked.userLikes.remove(userWhoUnlikes) #userLikes is the instance name in the Message model holding the many to many relationship
            messageBeingUnliked = Message.objects.get(id = messageId)
            if messageBeingUnliked.likeMessageCount > 0: #this prevents the subtraction when the user tries to unlike a message they have never liked initially
                messageBeingUnliked.likeMessageCount -= 1
                messageBeingUnliked.save()
                print("THIS IS THE LAST PRINT STATEMENT OF THE USER UNLIKES ROUTE THAT REDIRECTS TO LOGGED IN USER'S PAGE.")
        return redirect(reverse('home', args=(messageId,))) #using the name of the url to redirect and passing the variables/params to the form rendering the template
    else:
        print("You've never liked the message, so you cannot unlike it!")
        if userWhoUnlikes.id != messageBeingUnliked.userReceivesPost.id: #if this line of code runs it means the attemptive 'unliking' occurred on the specific user's page
            return redirect(reverse('specificUsersPage', args=(userFirstName, userLastName, userId, messageId,))) #using the name of the url to redirect and passing the variables/params to the form rendering the template
        else:
            return redirect(reverse('home', args=(messageId,))) #using the name of the url to redirect and passing the variables/params to the form rendering the template

def userLikesOnWall(request, messageId):
    print("THIS IS WHEN THE USER LIKES ROUTE ON THE WALL")
    print("*"*50)
    print("THIS IS THE MESSAGE ID:",messageId)
    print("*"*50)
    # print("This is the specific message being liked")
    messageBeingLiked = Message.objects.get(id=messageId)
    print(messageBeingLiked) #prints as a Message Object(#)
    print("This is the user liking the message")
    userWhoLikes = User.objects.get(id=request.session['loginInfo'])
    print(userWhoLikes) # prints as a User Object(#)
    # print("The id of the user giving the like", userWhoLikes.id)
    print("The id of the user receiving the like(the person who wrote the post)", messageBeingLiked.user.id)
    # print("The id of the users who have liked messages:", messageBeingLiked.userLikes.all())
    if userWhoLikes in messageBeingLiked.userLikes.all():
        print("You've already liked the message!")
        return redirect('/wall') #using the name of the url to redirect and passing the variables/params to the form rendering the template
    else:
        messageBeingLiked.userLikes.add(userWhoLikes) #This creates the like - userLikes is the instance name in the Message model holding the many to many relationship
        messageBeingLiked.likeMessageCount += 1
        messageBeingLiked.save()
        print("THIS IS THE LAST PRINT STATEMENT OF THE USER LIKES ON THE WALL ROUTE")
        return redirect('/wall')

def userUnlikesOnWall(request, messageId):
    print("THIS IS THE USER UNLIKES ROUTE ON THE WALL")
    print("*"*50)
    print("THIS IS THE MESSAGE ID:",messageId)
    print("*"*50)
    # print("This is the specific message being liked")
    messageBeingUnliked = Message.objects.get(id=messageId)
    print(messageBeingUnliked) #prints as a Message Object(#)
    print("This is the user unliking the message")
    userWhoUnlikes = User.objects.get(id=request.session['loginInfo'])
    print(userWhoUnlikes) # prints as a User Object(#)
    # print("The id of the user giving the like", userWhoUnlikes.id)
    print("The id of the user receiving the like(the person who wrote the post)", messageBeingUnliked.user.id)
    # print("The id of the users who have liked messages:", messageBeingUnliked.userLikes.all())
    if userWhoUnlikes in messageBeingUnliked.userLikes.all(): #this checks if the logged in user has liked the specific message to begin with
        messageBeingUnliked.userLikes.remove(userWhoUnlikes) #userLikes is the instance name in the Message model holding the many to many relationship
        messageBeingUnliked = Message.objects.get(id = messageId)
        if messageBeingUnliked.likeMessageCount > 0: #this prevents the subtraction when the user tries to unlike a message they have never liked initially
            print("This is the amount of likes the message has:", messageBeingUnliked.likeMessageCount)
            messageBeingUnliked.likeMessageCount -= 1
            print("This is the amount of likes the message has after subtracting one:", messageBeingUnliked.likeMessageCount)
            messageBeingUnliked.save()
            print("THIS IS THE LAST PRINT STATEMENT OF THE USER LIKES ON THE WALL ROUTE")
        return redirect('/wall')

def sendFriendRequest(request, userFirstName='firstName', userLastName='lastName', userId=0):
    print("*"*50)
    print("THIS IS THE SEND A FRIEND REQUEST ROUTE")
    userWhoSentFriendRequest = User.objects.get(id=request.session['loginInfo']) 
    print("This prints the user object of the user sending the friend request(logged in user).", userWhoSentFriendRequest)
    userWhoReceivesRequest = User.objects.get(id=userId) #the recipient of the friend request #the user id is from the ajax data front side
    print("This prints the user object of the user receiving the friend request.", userWhoReceivesRequest)
    if userWhoSentFriendRequest in userWhoReceivesRequest.friends.all() and userWhoReceivesRequest in userWhoSentFriendRequest.friends.all():
        print("This print means the users are already friends withc each other.")
        return redirect("/home") 
    userWhoSentFriendRequest.friends.add(userWhoReceivesRequest) #this creates the friend request
    print("These are all the users the logged in user sent friend requests to:", userWhoSentFriendRequest.friends.all())
    pageLocationId = request.POST['pageLocation']
    print("This is the id of the page the user is currently on:", pageLocationId)
    pageLocation = User.objects.get(id=pageLocationId)
    print("This is the page location:", pageLocation)
    notifyUser = Notification.objects.create(user= userWhoReceivesRequest, friendRequest = userWhoSentFriendRequest) #This creates a notification for the user receiving the posted message
    print("This is the friend request notification:", notifyUser)
    userWhoReceivesRequest.notifications += 1
    userWhoReceivesRequest.save()
    if userWhoSentFriendRequest.id != pageLocation.id: #if this line of code runs it means the friend request occurred on the specific user's page
        print("This means the friend request is occuring on the specific user page.")
        return redirect(reverse('specificUsersPage', args=(pageLocation.firstName, pageLocation.lastName, pageLocation.id,)))
    else: 
        print("This means the friend request is occuring on the home page.")
    print("THIS IS THE LAST PRINT STATEMENT OF THE SEND A FRIEND REQUEST ROUTE.")
    print("*"*50)
    return redirect("/home") 

def removeFriendRequest(request, userFirstName='firstName', userLastName='lastName', userId=0, specificUserId=0):
    print("*"*50)
    print("THIS IS THE REMOVE A FRIEND REQUEST ROUTE")
    loggedInUser = User.objects.get(id=request.session['loginInfo']) #user who is removing the friend request
    userBeingRemoved = User.objects.get(id=userId) #the recipient of the friend request
    print("This is the user object being removed:", userBeingRemoved) #prints as a User Object(#)
    userFirstName = userBeingRemoved.firstName # need for params to reroute
    userLastName = userBeingRemoved.lastName # need for params to reroute
    userId = userBeingRemoved.id # need for params to reroute
    userWhoRequestFriendRemoval = loggedInUser
    print("This prints the user object of the user removing the friend request:", userWhoRequestFriendRemoval)
    if specificUserId:
        currentPageLocation = User.objects(id= specificUserId)
        print("This identifies the id of the location of where the user is currently browsing:", currentPageLocation)
    if userBeingRemoved in userWhoRequestFriendRemoval.friends.all():
        userWhoRequestFriendRemoval.friends.remove(userBeingRemoved) # When a friendship is established the user object displays in both users, so it would need to be removed in both users
    if userWhoRequestFriendRemoval in userBeingRemoved.friends.all():
        userBeingRemoved.friends.remove(userWhoRequestFriendRemoval)
        if userBeingRemoved.notifications >= 0:
            userBeingRemoved.notifications -= 1 # This removes the notification on the html and prevents it from displaying
            userBeingRemoved.save() 
            notificationRemoval = Notification.objects.filter(friendRequest_id= loggedInUser.id)
            notificationRemoval.delete()  # This removes the notification in the database
            print('This is the notification removal:', notificationRemoval)
    print("THIS IS THE LAST PRINT STATEMENT OF THE REMOVE A FRIEND REQUEST ROUTE.")
    print("*"*50)
    if specificUserId:
        return redirect(reverse('specificUsersPage', args=(currentPageLocation.firstName, currentPageLocation.lastName, currentPageLocation.id,))) #using the name of the url to redirect and passing the variables/params to the form rendering the template
    else:
        return redirect("/home")


def acceptFriendRequest(request, userFirstName='firstName', userLastName='lastName', userId=0, messageId = 0):
    print("THIS IS THE ACCEPT A FRIEND REQUEST ROUTE")
    # print("*"*50)
    userReceivesRequest = User.objects.get(id=request.session['loginInfo'])
    # print(userReceivesRequest) #prints as a User Object(#)
    userWhoSentFriendRequest = User.objects.get(id=userId) #the recipient of the friend request
    # print(userWhoSentFriendRequest) #prints as a User Object(#)
    idOfPageLocation = request.POST['userWhoReceivesPost'] #This identifies the location of where the user is currently browsing
    print("This identifies the id of the location of where the user is currently browsing", idOfPageLocation)
    currentPageLocation = User.objects.get(id= idOfPageLocation) #a hidden input containing the id of the specific user
    # print("This identifies the location of where the user is currently browsing", currentPageLocation)
    print("This is the user page the logged in user is currently on", currentPageLocation)
    userFirstName = currentPageLocation.firstName # need for params to reroute
    userId = currentPageLocation.id # need for params to reroute
    userLastName = userReceivesRequest.lastName # need for params to reroute
    if userWhoSentFriendRequest in userReceivesRequest.friends.all():
        print("You've already accepted the friend request!")
    else:
        print("This print statement means the friend request is being accepted")
        userWhoSentFriendRequest.friends.add(userReceivesRequest)
        userReceivesRequest.friends.add(userWhoSentFriendRequest)
        #need to remove the notification after accepting the friend request
        removeNotif = Notification.objects.get(user = userReceivesRequest, friendRequest = userWhoSentFriendRequest)
        removeNotif.delete()
        # print("These are all the users the logged in user accepted friend requests from/is now friends with:", userReceivesRequest.friends.all())
        userReceivesRequest.notifications -= 1
        userReceivesRequest.save()
        # print("*"*50)
        if currentPageLocation!= userReceivesRequest:
            print("THIS IS THE LAST PRINT STATEMENT OF THE SEND A FRIEND REQUEST ROUTE.")
            return redirect(reverse('specificUsersPage', args=(userFirstName, userLastName, userId,)))
        else: 
            print("THIS IS THE LAST PRINT STATEMENT OF THE SEND A FRIEND REQUEST ROUTE.")
        return redirect("/home")

def unfriend(request, userFirstName='firstName', userLastName='lastName', userId=0, messageId = 0, specificUserId=0):
    print("*"*50)
    print("THIS IS THE DELETE A FRIEND ROUTE")
    loggedInUser = User.objects.get(id=request.session['loginInfo'])
    print("This is the loggedInUser:", loggedInUser)
    userIdOfFriend = request.POST['userIdOfFriend']  #this is the id of the user who is being unfriended
    print("User id of friend:", userIdOfFriend)
    userBeingUnfriended = User.objects.get(id=userIdOfFriend) # this grabs the user object
    print("This is the user object of the friend being removed:", userBeingUnfriended)
    # postLocationForFriendRemoval = request.POST['postLocationForFriendRemoval'] #This identifies the id of the location of where the user is currently browsing
    # print("This is the post location for friend removal:", postLocationForFriendRemoval) # this is the id of the logged in user page
    pageLocationId = request.POST['pageLocation']
    print("This is the page location id:", pageLocationId)
    pageLocation = User.objects.get(id = pageLocationId)
    print("This is the page location:", pageLocation)
    loggedInUsersNotifs = Notification.objects.filter(user=loggedInUser)
    # print("These are the logged in user's notifs:", loggedInUsersNotifs)
    # print("These are the people a specific user sent friend requests to:", userWhoSentFriendRequest.friends.all())
    userBeingUnfriended.friends.remove(loggedInUser)  #Removes the friendship
    loggedInUser.friends.remove(userBeingUnfriended)
    loggedInUser.friends.remove(loggedInUser)
    loggedInUsersNotifs = Notification.objects.filter(user=loggedInUser)
    if loggedInUsersNotifs.exists():
        removeNotif = Notification.objects.get(user = loggedInUser, friendRequest = userBeingUnfriended)
        if removeNotif:
            removeNotif.delete() #also need to delete this object in the notification model
        if loggedInUser.notifications > 0:
            loggedInUser.notifications -= 1
            loggedInUser.save()
        # for notifs in loggedInUserNotifs:
            # print("Inside the for loop:", notifs.friendRequest
            # print("This prints the notifications of the logged in user in a query set:", loggedInUserNotifs)
    if loggedInUser == pageLocation:
        print("This means the logged in user is unfriending a user on their home page.")
        return redirect("/home")
    else:
        print("This means the unfriending is occuring on a different page than the logged in user and the user being unfriended. Current location:", pageLocation)
    print("THIS IS THE LAST PRINT STATEMENT OF THE REMOVE A FRIEND REQUEST ROUTE.")
    print("*"*50)
    return redirect(reverse('specificUsersPage', args=(pageLocation.firstName, pageLocation.lastName, pageLocation.id,))) #using the name of the url to redirect and passing the variables/params to the form rendering the template

def removeMessageNotification(request, userFirstName='firstName', userLastName='lastName', userId=0, messageId=0):
    print("THIS FUNCTION REMOVES A MESSAGE NOTIFICATION FROM THE NOTIFICATION COUNTER")
    loggedInUser = User.objects.get(id=request.session['loginInfo'])
    #the above three lines of are needed because despite the correct logic below, always reverting to -1
    if loggedInUser.notifications < 0:
        print("The notification counter is negative and needs to be reset to 0.")
        resetNotificationCounter = User.objects.filter(id=request.session['loginInfo']).update(notifications=0) 
    #the above three lins of is needed because despite the correct logic below, always reverting to -1
    print("This console log means the logged in user is viewing their notifications on a specific user's page or the home page.")
    userId = request.POST['pageLocationOfMessage']
    pageLocation = User.objects.get(id= userId)
    print("This is the user object of the page current on:", pageLocation)
    messageId = request.POST['idOfMessage']
    print("This is the message id", messageId)
    message = Message.objects.get(id=messageId)
    print("This is the message object:", message)
    messageNotification = Notification.objects.get(user_id = loggedInUser, message_id = message.id)
    print("This is the notification that was created from the message post:", messageNotification)
    changeHoverStatus = Notification.objects.get(user_id = loggedInUser, message_id = message.id)
    if changeHoverStatus.hover != 0:
        print("This means the message notification has already been hovered over.")
    else:
        changeHoverStatus.hover += 1
        changeHoverStatus.save()
        updateLoggedInUserNotifications = loggedInUser
        if updateLoggedInUserNotifications.notifications >= 0:
            print("The notification is at minimum 0.")
            updateLoggedInUserNotifications.notifications -= 1
            updateLoggedInUserNotifications.save()
    if loggedInUser.id == pageLocation.id:
        print("This means the logged in user is viewing their notifications on their home page.")
        return redirect("/home")
    else: 
        pageLocation != loggedInUser
        print("This means the logged in user is viewing their notifications on a specific user's page.")
        return redirect(reverse('specificUsersPage', args=(pageLocation.firstName, pageLocation.lastName, pageLocation.id,))) #using the name of the url to redirect and passing the variables/params to the form rendering the template

def removeCommentNotification(request, userFirstName='firstName', userLastName='lastName', userId=0, messageId=0, commentId=0):
    print("THIS FUNCTION REMOVES A NEW COMMENT NOTIFICATION FROM THE NOTIFICATION COUNTER")
    loggedInUser = User.objects.get(id=request.session['loginInfo'])
    userId = request.POST['pageLocationOfMessage']
    pageLocation = User.objects.get(id= userId)
    print("This is the user object of the page current on:", pageLocation)
    #the below three lines of code are needed because despite the correct logic below, always reverting to -1
    if loggedInUser != pageLocation:
        print("This console log means the logged in user is viewing their comment notifications on a specific user's page or the home page.")
    messageId = request.POST['idOfMessage']
    # print("This is the message id", messageId)
    message = Message.objects.get(id=messageId)
    # print("This is the message object:", message)
    commentId = request.POST['idOfComment']
    print("This is the comment id", commentId)
    comment = Comment.objects.get(id=commentId)
    print("This is the user object who recieves the comment:", comment.userReceivesComment)
    print("This is the comment object:", comment)
    userCommentingId = request.POST['userCommenting']
    print("This is the id of the user who is commenting:", userCommentingId)
    userCommenting = Comment.objects.get(user_id = userCommentingId, message_id = message.id, userReceivesComment_id = comment.userReceivesComment.id)
    print("This is the user object who is commenting:", userCommentingId)
    commentNotification = Notification.objects.get(user_id = loggedInUser, comment_id = commentId, commenter_id = userCommentingId)
    print("This is the notification that was created from the message post:", commentNotification)
    changeHoverStatus = commentNotification
    if changeHoverStatus.hover != 0:
        print("This means the message notification has already been hovered over.")
    else:
        changeHoverStatus.hover += 1
        changeHoverStatus.save()
        updateLoggedInUserNotifications = loggedInUser
        if updateLoggedInUserNotifications.notifications >= 0:
            print("The notification is at minimum 0.")
            updateLoggedInUserNotifications.notifications -= 1
            updateLoggedInUserNotifications.save()
    if loggedInUser.id == pageLocation.id:
        print("This means the logged in user is viewing their notifications on their home page.")
        return redirect("/home")
    else: 
        pageLocation != loggedInUser
        print("This means the logged in user is viewing their notifications on a specific user's page.")
        return redirect(reverse('specificUsersPage', args=(pageLocation.firstName, pageLocation.lastName, pageLocation.id,))) #using the name of the url to redirect and passing the variables/params to the form rendering the template

def removeCommentNotificationOnWall(request, commentId=0):
    print("THIS FUNCTION REMOVES A COMMENT NOTIFICATION FROM THE NOTIFICATION COUNTER ON THE WALL")
    loggedInUser = User.objects.get(id=request.session['loginInfo'])
    #the above three lines of are needed because despite the correct logic below, always reverting to -1
    if loggedInUser.notifications < 0:
        print("The notification counter is negative and needs to be reset to 0.")
        resetNotificationCounter = User.objects.filter(id=request.session['loginInfo']).update(notifications=0) 
    #the above three lines of is needed because despite the correct logic below, always reverting to -1
    commentId = commentId
    print("This is the commentId of the comment object" , commentId)
    comment = Comment.objects.get(id=commentId)
    print("This is the comment object:", comment)
    commentNotification = Notification.objects.get(user_id = loggedInUser, comment_id = comment.id, commenter_id = comment.user.id)
    print("This is the notification that was created from the comment post:", commentNotification)
    changeHoverStatus = commentNotification
    if changeHoverStatus.hover != 0:
        print("This means the friend request notification has already been hovered over.")
    else:
        changeHoverStatus.hover += 1
        changeHoverStatus.save()
        updateLoggedInUserNotifications = loggedInUser
        if updateLoggedInUserNotifications.notifications >= 0:
            print("The notification is at minimum 0")
            updateLoggedInUserNotifications.notifications -= 1
            updateLoggedInUserNotifications.save()
    return redirect("/wall")

def removeFriendRequestNotification(request, userFirstName='firstName', userLastName='lastName', userId=0):
    print("THIS FUNCTION REMOVES A FRIEND REQUEST NOTIFICATION FROM THE NOTIFICATION COUNTER")
    loggedInUser = User.objects.get(id=request.session['loginInfo'])
    #the above three lines of are needed because despite the correct logic below, always reverting to -1
    if loggedInUser.notifications < 0:
        print("The notification counter is negative and needs to be reset to 0.")
        resetNotificationCounter = User.objects.filter(id=request.session['loginInfo']).update(notifications=0) 
    #the above three lines of is needed because despite the correct logic below, always reverting to -1
    idOfPageLocation = request.POST['loggedInUser'] #id of the current page location
    print("This is the id of the page location:", idOfPageLocation)
    pageLocation = User.objects.get(id = idOfPageLocation)
    print("This is the current user page being viewed:", pageLocation)
    friendRequestId = request.POST['userIdOfFriend']
    friendRequest = User.objects.get(id = friendRequestId)
    print("This is the user who sent the friend request:", friendRequest)
    friendRequestNotification = Notification.objects.get(user_id = loggedInUser, friendRequest_id = friendRequest.id)
    print("This is the notification that was created from the friend request:", friendRequestNotification)
    changeHoverStatus = Notification.objects.get(user = loggedInUser, friendRequest = friendRequest)
    if changeHoverStatus.hover != 0:
        print("This means the friend request notification has already been hovered over.")
    else:
        changeHoverStatus.hover += 1
        changeHoverStatus.save()
        updateLoggedInUserNotifications = loggedInUser
        friendRequest.friends.remove(loggedInUser)
        friendRequest.friends.remove(friendRequest)
        loggedInUser.friends.remove(loggedInUser)
        if updateLoggedInUserNotifications.notifications >= 0:
            print("The notification is at minimum 0")
            updateLoggedInUserNotifications.notifications -= 1
            updateLoggedInUserNotifications.save()
    if loggedInUser.id == pageLocation.id:
        print("This means the logged in user is viewing their notifications on their home page.")
        return redirect("/home")
    else:
        print("This means the logged in user is viewing their notifications on a specific user's page.")
        return redirect(reverse('specificUsersPage', args=(pageLocation.firstName, pageLocation.lastName, pageLocation.id,))) #using the name of the url to redirect and passing the variables/params to the form rendering the template

def removeFriendRequestNotificationOnWall(request):
    print("THIS FUNCTION REMOVES A FIREND REQUEST NOTIFICATION FROM THE NOTIFICATION COUNTER ON THE WALL")
    loggedInUser = User.objects.get(id=request.session['loginInfo'])
    #the above three lines of are needed because despite the correct logic below, always reverting to -1
    if loggedInUser.notifications < 0:
        print("The notification counter is negative and needs to be reset to 0.")
        resetNotificationCounter = User.objects.filter(id=request.session['loginInfo']).update(notifications=0) 
    #the above three lines of is needed because despite the correct logic below, always reverting to -1
    print("This console log means the logged in user is viewing their notifications on a specific user's page or the home page.")
    # pageLocation = request.POST['pageLocation']
    # print("This is the user object of the page current on:", pageLocation)
    newFriendRequest = request.POST['userIdOfFriend']
    print("This is the user who sent the friend request:", newFriendRequest)
    friendRequestNotification = Notification.objects.get(user_id = loggedInUser, friendRequest_id = newFriendRequest)
    print("This is the notification that was created from the friend request:", friendRequestNotification)
    changeHoverStatus = Notification.objects.get(user = loggedInUser, friendRequest = newFriendRequest)
    if changeHoverStatus.hover != 0:
        print("This means the friend request notification has already been hovered over.")
    else:
        changeHoverStatus.hover += 1
        changeHoverStatus.save()
        updateLoggedInUserNotifications = loggedInUser
        if updateLoggedInUserNotifications.notifications >= 0:
            print("The notification is at minimum 0")
            updateLoggedInUserNotifications.notifications -= 1
            updateLoggedInUserNotifications.save()
    return redirect("/wall")

def removeMessageNotificationOnWall(request, messageId=0):
    print("THIS FUNCTION REMOVES A MESSAGE NOTIFICATION FROM THE NOTIFICATION COUNTER ON THE WALL")
    loggedInUser = User.objects.get(id=request.session['loginInfo'])
    #the above three lines of are needed because despite the correct logic below, always reverting to -1
    if loggedInUser.notifications < 0:
        print("The notification counter is negative and needs to be reset to 0.")
        resetNotificationCounter = User.objects.filter(id=request.session['loginInfo']).update(notifications=0) 
    #the above three lines of is needed because despite the correct logic below, always reverting to -1
    messageId = messageId
    print("This is the messageId of the message object" , messageId)
    message = Message.objects.get(id=messageId)
    print("This is the message object:", message)
    messageNotification = Notification.objects.get(user_id = loggedInUser, message_id = message.id)
    print("This is the notification that was created from the message post:", messageNotification)
    changeHoverStatus = messageNotification
    print("This is the hover status of the message notification:", changeHoverStatus.hover)
    if changeHoverStatus.hover == 1:
        print("This means the message notification has already been hovered over.")
    else:
        print("This is the notification that was created from the message post:", messageNotification)
        changeHoverStatus.hover += 1
        changeHoverStatus.save()
        updateLoggedInUserNotifications = loggedInUser
        if updateLoggedInUserNotifications.notifications >= 0:
            print("The notification is at minimum 0")
            updateLoggedInUserNotifications.notifications -= 1
            updateLoggedInUserNotifications.save()    
    return redirect("/wall")

def clearAllNotifications(request):
    print("THIS FUNCTION CLEARS ALL THE NOTIFICATIONS THE LOGGED IN USER HAS")
    loggedInUser = User.objects.get(id=request.session["loginInfo"])
    removeMessageNotifications = Notification.objects.filter(user= loggedInUser)
    print("These are the message notifications that will be removed:", removeMessageNotifications)
    if removeMessageNotifications:
        removeMessageNotifications.delete()
    # removCommentNotifications = Notification.objects.filter(user= loggedInUser)
    # print("These are the comment notifications that will be removed:", removCommentNotifications)
    # if removCommentNotifications:
    #     removCommentNotifications.delete()
    removeFriendRequestNotifications = Notification.objects.filter(friendRequest= loggedInUser)
    print("These are the friend request notifications that will be removed:", removeFriendRequestNotifications)
    if removeFriendRequestNotifications:
        removeFriendRequestNotifications.delete()
    resetNotificationCounter = User.objects.filter(id=request.session['loginInfo']).update(notifications=0) 
    print("THIS IS THE LAST PRINT STATEMENT IN THE CLEAR ALL NOTIFICATIONS")
    return redirect("/home")

def searchForUsersProfile(request):
    print("THIS IS THE SEARCH FOR A USER PROFILE ROUTE")
    loggedInUser = User.objects.get(id=request.session["loginInfo"])
    try: #used so i can incoperate 'except index error' in case the logged in user triggers an index error searching for a user not in the database
        if request.method == 'GET':
            # searchForUser = request.GET.get("searchBarInput")
            searchForUser = request.GET.get("searchBarInput")
            if searchForUser == '':
                print("No search submitted.") 
                id = loggedInUser.id #sends them back to their page
            searchForUser = request.GET.get('searchBarInput').split() #creates a list of arrays with the names submitted by the logged in user
            if searchForUser is not None: #use to prevent NoneType object attribute split error
            # print("The name(s) the logged in user typed", searchForUser)
                for name in searchForUser: # have to iterate to use title on a list
                    print("The name(s) searched:", name.title())
                    if len(searchForUser) == 1:
                        searchedNameOne = name.title() #title capitalizes the submitted data
                        print("This means there was only one name submitted", searchedNameOne)
                        id = User.objects.filter(Q(firstName = (searchedNameOne))| Q(lastName= (searchedNameOne))).values('id')[0]['id']
                    if len(searchForUser) > 1:
                        searchedNameOne = searchForUser[0].title()
                        searchedNameTwo = searchForUser[1].title()
                        print("This means there was two names submitted", searchedNameOne, searchedNameTwo)
                        id = User.objects.filter(Q(firstName = (searchedNameOne))| Q(lastName= (searchedNameTwo))| Q(firstName = (searchedNameTwo))| Q(lastName= (searchedNameOne))).values('id')[0]['id'] #switched the order to include all ways the user typers their search
                userProfile = User.objects.get(id = id) #this retrieves the searched user as an object
                userProfile.firstName
                userProfile.lastName
                print("This is the searched user's first name, last name, and id:", userProfile.firstName, userProfile.lastName, userProfile.id)
                print("THIS IS THE LAST PRINT STATEMENT OF THE SEARCH FOR A USER PROFILE ROUTE")
                return redirect(reverse('specificUsersPage', args=(userProfile.firstName, userProfile.lastName, userProfile.id,))) #using the name of the url to redirect and passing the variables/params to the form rendering the template
        else:
            print("This means it is empty")
    except IndexError:
        print("No results found!")
    context = {
        'loggedInUser': User.objects.get(id=request.session['loginInfo']),
        'allUsers': User.objects.all().exclude(id=request.session['loginInfo']).order_by('firstName'), #orders alphabetically
        'searchForUser': searchForUser,
        'notifications': Notification.objects.all,
        'loggedInUsersNotifs': Notification.objects.filter(user=loggedInUser)
    }
    return render(request, "noUserFound.html", context)

def logout(request):
    request.session.clear()
    return redirect('/')