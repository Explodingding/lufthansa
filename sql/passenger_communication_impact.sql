-- Question:
-- Which passenger communication channels are most active around disrupted flights?

SELECT
    route,
    event_type,
    channel,
    event_count,
    delayed_flight_events,
    cancelled_flight_events,
    ROUND(delayed_flight_events / NULLIF(event_count, 0) * 100, 2) AS delayed_event_share_pct,
    ROUND(cancelled_flight_events / NULLIF(event_count, 0) * 100, 2) AS cancelled_event_share_pct
FROM gold_passenger_communication
ORDER BY
    delayed_flight_events DESC,
    cancelled_flight_events DESC,
    event_count DESC,
    route,
    event_type,
    channel;
