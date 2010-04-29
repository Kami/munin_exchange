import markdown

from django.shortcuts import render_to_response, get_object_or_404, HttpResponse, HttpResponseRedirect, Http404
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt

from django.contrib.comments.models import Comment

from forms import ProfileForm

def index(request):
	return render_to_response('index.html', {}, \
							context_instance = RequestContext(request))

@csrf_exempt
def markdown_preview(request):
	if not request.POST:
		raise Http404()
	
	try:
		data = request.POST['data']
	except KeyError:
		raise Http404()
	
	data_formatted = markdown.markdown(data)
	return render_to_response('core/markdown_preview.html', {'data': data_formatted}, \
													context_instance = RequestContext(request))		
	
@login_required
def profile(request):
	'''
	Displays page where user can update their profile.
	
	@param request: Django request object.
	@return: Rendered profile.html.
	'''
	if request.method == 'POST':
		form = ProfileForm(request.POST)
		if form.is_valid():
			data = form.cleaned_data
			print data

			#Update user with form data
			request.user.first_name = data['first_name']
			request.user.last_name = data['last_name']
			request.user.email = data['email']
			request.user.save()

			messages.success(request, 'Successfully updated profile!')
	else: 
		#Try to pre-populate the form with user data.
		form = ProfileForm(initial = {
			'first_name': request.user.first_name,
			'last_name': request.user.last_name,
			'email': request.user.email,
		})

	return render_to_response('django_rpx_plus/profile.html', {
								'form': form,
								'user': request.user,
							  },
							  context_instance = RequestContext(request))
	
def get_latest_comments(count = 4):
	""" Returns the latest comments."""
	comments = Comment.objects.filter(is_public = True).order_by('-submit_date')[:count]
	
	return comments