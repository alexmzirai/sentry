from __future__ import absolute_import

from rest_framework.response import Response

from sentry.api.bases import OrganizationEventsEndpointBase, OrganizationEventsError, NoProjects
from sentry.utils.snuba import raw_query


class OrganizationEventsMetaEndpoint(OrganizationEventsEndpointBase):

    def get(self, request, organization):
        try:
            snuba_args = self.get_snuba_query_args(request, organization)
        except OrganizationEventsError as exc:
            return Response({'detail': exc.message}, status=400)
        except NoProjects:
            return Response({'count': 0})

        data = raw_query(
            aggregations=[['count()', '', 'count']],
            referrer='api.organization-event-meta',
            turbo=True,
            **snuba_args
        )['data'][0]

        return Response({
            # this needs to be multiplied to account for the `TURBO_SAMPLE_RATE`
            # in snuba
            'count': data['count'] * 10,
        })
