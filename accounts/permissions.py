from rest_framework import permissions


class IsOwner(permissions.BasePermission):
    """Permission to only allow owners of an object to edit it."""

    def has_object_permission(self, request, view, obj):
        return obj == request.user or obj.user == request.user


class IsHost(permissions.BasePermission):
    """Permission to only allow hosts."""

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_host


class IsGuest(permissions.BasePermission):
    """Permission to only allow guests."""

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_guest





