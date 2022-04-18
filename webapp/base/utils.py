def generate_metric_value(post, metric_format, request_data):
    metrics = (
        post.postmetricsdaily_set.filter(
            # end_time__gte=request_data.get('start'),
            #    end_time__lte=request_data.get('end'),
        )
        .order_by("-end_time")
        .values("metrics__metric", "value")
    )
    if metrics:
        output = {}
        for metric in metrics:
            k = metric_format.get(metric.get("metrics__metric"))
            if k in output:
                continue
            else:
                output[k] = metric["value"]
        return output

    return {key: 0 for key in metric_format.values()}
