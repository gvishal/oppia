# coding: utf-8

# Copyright 2015 The Oppia Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS-IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Controllers for the collections editor."""

__author__ = 'Abraham Mgowano'

from core.controllers import base
from core.domain import collection_services
from core.domain import config_domain
from core.domain import rights_manager
from core.platform import models
current_user_services = models.Registry.import_current_user_services()
import utils


def _require_valid_version(version_from_payload, collection_version):
    """Check that the payload version matches the given collection version."""
    if version_from_payload is None:
        raise base.BaseHandler.InvalidInputException(
            'Invalid POST request: a version must be specified.')

    if version_from_payload != collection_version:
        raise base.BaseHandler.InvalidInputException(
            'Trying to update version %s of collection from version %s, '
            'which is too old. Please reload the page and try again.'
            % (collection_version, version_from_payload))


def require_editor(handler):
    """Decorator that checks if the user can edit the given collection."""
    def test_collection_editor(self, collection_id, **kwargs):
        """Gets the user and collection id if the user can edit it.

        Args:
            self: the handler instance
            collection_id: the collection id
            **kwargs: any other arguments passed to the handler

        Returns:
            The relevant handler, if the user is authorized to edit this
            collection.

        Raises:
            self.PageNotFoundException: if no such collection exists.
            self.UnauthorizedUserException: if the user exists but does not
                have the right credentials.
        """
        if not self.user_id:
            self.redirect(current_user_services.create_login_url(
                self.request.uri))
            return

        if self.username in config_domain.BANNED_USERNAMES.value:
            raise self.UnauthorizedUserException(
                'You do not have the credentials to access this page.')

        try:
            collection_services.get_collection_by_id(collection_id)
        except:
            raise self.PageNotFoundException

        if not rights_manager.Actor(self.user_id).can_edit(
                rights_manager.ACTIVITY_TYPE_COLLECTION, collection_id):
            raise self.UnauthorizedUserException(
                'You do not have the credentials to edit this collection.',
                self.user_id)

        return handler(self, collection_id, **kwargs)

    return test_collection_editor


class CollectionEditorHandler(base.BaseHandler):
    """Base class for all handlers for the collection editor page."""

    # The page name to use as a key for generating CSRF tokens.
    PAGE_NAME_FOR_CSRF = 'collection_editor'


class CollectionEditorPage(CollectionEditorHandler):
    """The editor page for a single collection."""

    def get(self, collection_id):
        """Handles GET requests."""

        collection = collection_services.get_collection_by_id(
            collection_id, strict=False)

        if (collection is None or
            not rights_manager.Actor(self.user_id).can_view(
                rights_manager.ACTIVITY_TYPE_COLLECTION, collection_id)):
            self.redirect('/')
            return

        can_edit = (
            bool(self.user_id) and
            self.username not in config_domain.BANNED_USERNAMES.value and
            rights_manager.Actor(self.user_id).can_edit(
                rights_manager.ACTIVITY_TYPE_COLLECTION, collection_id))

        self.values.update({
            'can_edit': can_edit,
            'collection_id': collection.id,
            'title': collection.title
        })

        self.render_template('collection_editor/collection_editor.html')


class WritableCollectionDataHandler(CollectionEditorHandler):
    """A data handler for collections which supports writing."""

    @require_editor
    def put(self, collection_id):
        """Updates properties of the given collection."""

        collection = collection_services.get_collection_by_id(collection_id)
        version = self.payload.get('version')
        _require_valid_version(version, collection.version)

        commit_message = self.payload.get('commit_message')
        change_list = self.payload.get('change_list')

        try:
            collection_services.update_collection(
                self.user_id, collection_id, change_list, commit_message)
        except utils.ValidationError as e:
            raise self.InvalidInputException(e)

        # Retrieve the updated collection.
        try:
            collection_dict = (
                collection_services.get_learner_collection_dict_by_id(
                    collection_id, self.user_id))
        except:
            raise self.PageNotFoundException

        # Send the updated collection back to the frontend.
        self.values.update(collection_dict)
        self.render_json(self.values)