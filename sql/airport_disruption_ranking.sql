-- Question:
-- Which origin airports contribute most to departure disruption?

SELECT
    origin_airport,
    airport_name,
    city,
    country,
    total_departures,
    delayed_departures,
    cancelled_departures,
    ROUND(delay_rate * 100, 2) AS delay_rate_pct,
    ROUND(average_departure_delay_minutes, 2) AS average_departure_delay_minutes
FROM gold_airport_disruption
WHERE total_departures > 0
ORDER BY
    delay_rate DESC,
    cancelled_departures DESC,
    average_departure_delay_minutes DESC,
    origin_airport;
