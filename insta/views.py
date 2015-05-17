from django.shortcuts import render
from django.conf import settings
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
import requests
try:
    import json
except ImportError:
    import simplejson as json

from django.contrib.sites.models import Site

from instagram.client import InstagramAPI
from instagram import subscriptions

from insta.models import InstaPost, IGTag, BadPerson, Location



def challenger(request):
    mode = request.values.get('hub.mode')
    challenge = request.values.get('hub.challenge')
    verify_token = request.values.get('hub.verify_token')
    if challenge:
        return Response(challenge)
    else:
        pass

def get_location_details(request, location_id):
    client_id = settings.IG_CLIENT_ID
    client_secret = settings.IG_CLIENT_SECRET
    api = InstagramAPI(client_id=client_id, client_secret=client_secret)
    
    try:
	    iglo = api.location(location_id)
	    loclo = Location.objects.get(location_id=location_id)
	    loclo.name = iglo.name
	    loclo.latitude = iglo.point.latitude
	    loclo.longitude = iglo.point.longitude
	    
	    loclo.save()
	    messages.success(request, "IG location retrieval successful." )
    except:
        messages.error(request, "error retrieving IG location." )
    
    if 'HTTP_REFERER' in request.META:
        return HttpResponseRedirect(request.META['HTTP_REFERER'])
    else:
        return HttpResponseRedirect('/')
        



def instagram_subscribe(request, object, object_id):
    client_id = settings.IG_CLIENT_ID
    client_secret = settings.IG_CLIENT_SECRET
    api = InstagramAPI(client_id=client_id, client_secret=client_secret)
    current_site = Site.objects.get_current()

    

    if settings.DEBUG == True:
        protocol = 'https://' #for localtunnel dev use
    else:
        protocol = 'http://' #production use

    callback = ''.join([protocol, current_site.domain, '/instagram/hook/'])
    

    sun = api.create_subscription(object=object, object_id=object_id, aspect='media',
                            callback_url=callback)
    
    if object == 'tag':
        ig_id = sun['data']['id']
        tag_instance = IGTag.objects.get(tag=object_id)
        tag_instance.ig_id = ig_id
        tag_instance.save()
    else:
        subscription_id = sun['data']['id']
        location_instance = Location.objects.get(location_id=object_id)
        location_instance.subscription_id = subscription_id
        location_instance.save()

    code = sun['meta']['code']
    if code == 200:
        messages.success(request, "IG subscription successful." )
    else:
        messages.error(request, "error with subscription." )
    reactor = subscriptions.SubscriptionsReactor()
    reactor.register_callback(subscriptions.SubscriptionType.TAG, process_tag_update)
    if 'HTTP_REFERER' in request.META:
        return HttpResponseRedirect(request.META['HTTP_REFERER'])
    else:
        return HttpResponseRedirect('/')

    
def get_media(object, object_id, subscription_id):
    client_id = settings.IG_CLIENT_ID
    client_secret = settings.IG_CLIENT_SECRET
    api = InstagramAPI(client_id=client_id, client_secret=client_secret)
    if object == 'tag':
        try:
            tag_instance = IGTag.objects.get(ig_id=subscription_id)
            tag = tag_instance.tag
            
            tag_recent_media, next_ = api.tag_recent_media(3, 0, tag)
            ban_list = []
            try:
                banned_people = BadPerson.objects.all() #summon ban list
                for obj in banned_people:
                    ban_list.append(obj.username)
            except:
                pass
            for media in tag_recent_media:
                obj, created = InstaPost.objects.get_or_create(insta_id=media.id)
               
                obj.username = media.user.username
                obj.link = media.link
                obj.thumbnail = media.images['thumbnail'].url
                obj.standard_resolution = media.images['standard_resolution'].url
                obj.caption_text = media.caption.text
                obj.profile_picture = media.user.profile_picture
                obj.created_time = media.created_time

                obj.tag = tag_instance
                try:
                    ig_location_id = media.location.id
                    
                    loc, created = Location.objects.get_or_create(location_id=ig_location_id)
                    if created:
                       
                        loc.name = media.location.name
                        loc.latitude = media.location.point.latitude
                        loc.longitude = media.location.point.latitude
                        loc.save()
                        obj.location = Location.objects.get(location_id=ig_location_id)
                        obj.save()
                    
                    else:
                       
                        loc.name = media.location.name
                        loc.latitude = media.location.point.latitude
                        loc.longitude = media.location.point.longitude
                        loc.save()
                        obj.location = Location.objects.get(location_id=ig_location_id)
                        obj.save()
                        continue
                except:
                    pass

                obj.save()
                
        except:
            print "get media exception"
            pass
    elif object == 'location':
        
        loc_recent_media, next_ = api.location_recent_media(5, 9999999999999999999, object_id) #wtf
        
        ban_list = []
        try:
            banned_people = BadPerson.objects.all() #summon ban list
            for obj in banned_people:
                ban_list.append(obj.username)
        except:
            pass
        for media in loc_recent_media:
            obj, created = InstaPost.objects.get_or_create(insta_id=media.id)
            
            obj.username = media.user.username
            obj.link = media.link
            obj.thumbnail = media.images['thumbnail'].url
            obj.standard_resolution = media.images['standard_resolution'].url
            if media.caption.text:
                obj.caption_text = media.caption.text
            obj.profile_picture = media.user.profile_picture
            obj.created_time = media.created_time
            ig_location_id = media.location.id
            location_instance = Location.objects.get(location_id=ig_location_id)
            obj.location = location_instance
            obj.save()

    else:
        print "unsupported object"
        pass


def search_media(request, tag):
    client_id = settings.IG_CLIENT_ID
    client_secret = settings.IG_CLIENT_SECRET
    api = InstagramAPI(client_id=client_id, client_secret=client_secret)
    tag_recent_media, next_ = api.tag_recent_media(50, 0, tag)
    ban_list = []
    try:
        banned_people = BadPerson.objects.all() #summon ban list
        for obj in banned_people:
            ban_list.append(obj.username)
    except:
        pass
    try:
        tag_instance = IGTag.objects.get(tag=tag)
        for media in tag_recent_media:
            obj, created = InstaPost.objects.get_or_create(insta_id=media.id)
            
            obj.username = media.user.username
            obj.link = media.link
            obj.thumbnail = media.images['thumbnail'].url
            obj.standard_resolution = media.images['standard_resolution'].url
            obj.caption_text = media.caption.text
            obj.profile_picture = media.user.profile_picture
            obj.created_time = media.created_time
            obj.tag = tag_instance
           
            try:
                ig_location_id = media.location.id
                
                loc, created = Location.objects.get_or_create(location_id=ig_location_id)
                if created:
                    
                    loc.name = media.location.name
                    loc.latitude = media.location.point.latitude
                    loc.longitude = media.location.point.latitude
                    loc.save()
                    obj.location = Location.objects.get(location_id=ig_location_id)
                    obj.save()
                
                else:
                    
                    loc.name = media.location.name
                    loc.latitude = media.location.point.latitude
                    loc.longitude = media.location.point.longitude
                    loc.save()
                    obj.location = Location.objects.get(location_id=ig_location_id)
                    obj.save()
                    
                    continue
            except:
                pass
            
            obj.save()
    except:
        print "search media exception"
        pass

    if 'HTTP_REFERER' in request.META:
        return HttpResponseRedirect(request.META['HTTP_REFERER'])
    else:
        return HttpResponseRedirect('/')

def hide_media(request, insta_id):
    try:
        post_instance = InstaPost.objects.get(insta_id=insta_id)
        post_instance.delete()
    except:
        pass

    if 'HTTP_REFERER' in request.META:
        return HttpResponseRedirect(request.META['HTTP_REFERER'])
    else:
        return HttpResponseRedirect('/')


@csrf_exempt
def process_tag_update(request):
    if request.method == "GET":
        mode = request.GET.get("hub.mode")
        challenge = request.GET.get("hub.challenge")
        verify_token = request.GET.get("hub.verify_token")
        return HttpResponse(challenge)
    if request.method == "POST":
        data = json.loads(request.body)
        for i in data:
            
            object = i['object']
            object_id = i['object_id']
            subscription_id = i['subscription_id']
            get_media(object, object_id, subscription_id)
        
        
        print data
        return HttpResponseRedirect('/') 



# def instagram_subscribe(request, tag):
#     client_id = settings.IG_CLIENT_ID
#     client_secret = settings.IG_CLIENT_SECRET
#     api = InstagramAPI(client_id=client_id, client_secret=client_secret)
#     current_site = Site.objects.get_current()
#     if settings.DEBUG == True:
#         protocol = 'https://' #for localtunnel dev use
#     else:
#         protocol = 'http://' #production use

#     callback = ''.join([protocol, current_site.domain, '/instagram/hook/'])
    

#     sun = api.create_subscription(object='tag', object_id=tag, aspect='media',
#                             callback_url=callback)
    
#     ig_id = sun['data']['id']
#     tag_instance = IGTag.objects.get(tag=tag)
#     tag_instance.ig_id = ig_id
#     tag_instance.save()
#     code = sun['meta']['code']
#     if code == 200:
#         messages.success(request, "IG subscription successful." )
#     else:
#         messages.error(request, "error with subscription." )
#     reactor = subscriptions.SubscriptionsReactor()
#     reactor.register_callback(subscriptions.SubscriptionType.TAG, process_tag_update)
#     if 'HTTP_REFERER' in request.META:
#         return HttpResponseRedirect(request.META['HTTP_REFERER'])
#     else:
#         return HttpResponseRedirect('/')

def delete_igsubscription(request, object, object_id):
    client_id = settings.IG_CLIENT_ID
    client_secret = settings.IG_CLIENT_SECRET

    api = InstagramAPI(client_id=client_id, client_secret=client_secret)
    if object == 'tag':
        
        try:
            tag_instance = IGTag.objects.get(tag=object_id)
            ig_id = tag_instance.ig_id
            tag_instance.ig_id = None
            tag_instance.save()
            de = api.delete_subscriptions(id=ig_id)
            code = de['meta']['code']
            if code == 200:
                messages.success(request, "IG subscription successfully removed." )
            else:
                messages.error(request, "Error removing subscription" )
        except:
            messages.error(request, "Looks like it wasn't subscribed in the first place" )
            pass
    else:
        try:
            location_instance = Location.objects.get(location_id=object_id)
            subscription_id = location_instance.subscription_id
       
            de = api.delete_subscriptions(id=subscription_id)
            code = de['meta']['code']
            if code == 200:
                messages.success(request, "IG subscription successfully removed." )
                location_instance.subscription_id = None
                location_instance.save()
            else:
                messages.error(request, "Error removing subscription" )
        except:
            messages.error(request, "Looks like it wasn't subscribed in the first place" )
            pass
    

    if 'HTTP_REFERER' in request.META:
        return HttpResponseRedirect(request.META['HTTP_REFERER'])
    else:
        return HttpResponseRedirect('/')
