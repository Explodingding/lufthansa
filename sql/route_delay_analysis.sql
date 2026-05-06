-- Question:
-- Which routes have the highest delay impact and should be reviewed first?

WITH ranked_routes AS (
    SELECT
        route,
        total_flights,
        delayed_flights,
        cancelled_flights,
        ROUND(delay_rate * 100, 2) AS delay_rate_pct,
        ROUND(average_departure_delay_minutes, 2) AS average_departure_delay_minutes,
        RANK() OVER (
            ORDER BY delay_rate DESC, average_departure_delay_minutes DESC
        ) AS disruption_rank
    FROM gold_route_performance
    WHERE total_flights > 0
)

SELECT
    route,
    disruption_rank,
    total_flights,
    delayed_flights,
    cancelled_flights,
    delay_rate_pct,
    average_departure_delay_minutes
FROM ranked_routes
ORDER BY disruption_rank, route;
