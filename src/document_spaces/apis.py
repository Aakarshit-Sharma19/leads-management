from typing import Any

from django.contrib.auth import get_user_model
from ninja import NinjaAPI
from ninja.security import django_auth

from document_spaces.schemas import ManagerRequest, WriterRequest, ErrorResponse
from leads_data.models import DocumentSpace

User = get_user_model()
spaces_api = NinjaAPI(urls_namespace='spaces_api', csrf=True)


@spaces_api.post('manager/', auth=django_auth, url_name='spaces_manager',
                 response={200: Any, 400: ErrorResponse, 403: ErrorResponse})
def add_manager_to_space(request, manager_req: ManagerRequest):
    if not hasattr(request.auth, 'owner_of_space'):
        return 403, {'message': 'You are not authorized to make changes to the space'}
    space: DocumentSpace = request.auth.owner_of_space
    try:
        manager = User.objects.get(email=manager_req.email)
        if manager.is_space_owner:
            return 400, {'message': 'The user who is an owner of a space cannot be added to the other space as manager.'}
    except User.DoesNotExist:
        return 400, {'message': 'The user does not exist'}
    if space.managers.filter(pk=manager.pk).exists():
        changed = False
    else:
        space.managers.add(manager)
        changed = True
    return {
        'message': f'The user {manager.get_full_name()} has been successfully added to your space',
        'user': {
            'name': manager.get_full_name(),
            'email': manager.email
        },
        'changed': changed
    }


@spaces_api.delete('manager/', auth=django_auth, url_name='spaces_manager',
                   response={200: Any, 400: ErrorResponse, 403: ErrorResponse})
def remove_manager_from_space(request, manager_req: ManagerRequest):
    if not hasattr(request.auth, 'owner_of_space'):
        return 403, {'message': 'You are not authorized to make changes to the space'}
    space: DocumentSpace = request.auth.owner_of_space
    try:
        manager = User.objects.get(email=manager_req.email)
    except User.DoesNotExist:
        return 400, {'message': 'The user does not exist'}
    space.managers.remove(manager)
    return {
        'message': f'The user {manager.get_full_name()} has been successfully removed from your space',
    }


@spaces_api.post('writer/', auth=django_auth, url_name='spaces_writer',
                 response={200: Any, 400: ErrorResponse, 403: ErrorResponse})
def add_writer_to_space(request, writer_req: WriterRequest):
    if not hasattr(request.auth, 'owner_of_space'):
        return 403, {'message': 'You are not authorized to make changes to the space'}

    space: DocumentSpace = request.auth.owner_of_space
    try:
        writer = User.objects.get(email=writer_req.email)
        if writer.is_space_owner:
            return 400, {'message': 'The user who is an owner of a space cannot be added to the other space as writer.'}
    except User.DoesNotExist:
        return 400, {'message': 'The user does not exist'}

    if space.writers.filter(pk=writer.pk).exists():
        changed = False
    else:
        space.writers.add(writer)
        changed = True

    return {
        'message': f'The user {writer.get_full_name()} has been successfully added to your space',
        'user': {
            'name': writer.get_full_name(),
            'email': writer.email
        },
        'changed': changed
    }


@spaces_api.delete('writer/', auth=django_auth, url_name='spaces_writer',
                   response={200: Any, 400: ErrorResponse, 403: ErrorResponse})
def remove_writer_from_space(request, writer_req: WriterRequest):
    if not hasattr(request.auth, 'owner_of_space'):
        return 403, {'message': 'You are not authorized to make changes to the space'}
    space: DocumentSpace = request.auth.owner_of_space
    try:
        writer = User.objects.get(email=writer_req.email)
    except User.DoesNotExist:
        return 400, {'message': 'The user does not exist'}
    space.writers.remove(writer)
    return {
        'message': f'The user {writer.get_full_name()} has been successfully removed from your space',
    }
