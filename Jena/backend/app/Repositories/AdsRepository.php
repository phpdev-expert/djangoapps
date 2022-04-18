<?php

namespace App\Repositories;

use App\Ads;
use App\Category;
use Illuminate\Support\Facades\DB;
use Illuminate\Database\Eloquent\Model;

class AdsRepository implements RepositoryInterface
{
    // model property on class instances
    protected $model;

    // Constructor to bind model to repo
    public function __construct(Model $model)
    {
        $this->model = $model;
    }

    // Get all instances of model
    public function all()
    {
        return $this->model
            ->where('status', '=', '0')
            ->where('user_id', '=', Auth()->user()->id)
            ->paginate(100);
    }

    // create a new record in the database
    public function create(array $data)
    {
        return $this->model->create($data);
    }

    // update record in the database
    public function update(array $data, $id)
    {
        $record = $this->model->find($id);
        return $record->update($data);
    }

    // remove record from the database
    public function delete($id)
    {
        return $this->model->destroy($id);
    }

    // show the record with the given id
    public function show($id)
    {
        return $this->model->findOrFail($id);
    }

    // search for queries
    public function search($id = '0' , $search = "")
    {
        $searchCount = strlen(trim($search));
        if(!$id && $id === '0' && $searchCount <= 0) {
            return $query = Ads::paginate(10);
        }

        $query = Ads::select('*');
        
        if ($id > 0) {
            $query = Ads::Join('ads_category', function($join) {
                $join->on('ads.id', '=', 'ads_category.ads_id');
            })
            ->where('ads_category.category_id','=', $id);
        }

        if ($searchCount > 0) {
            $query->where('ads.title', 'LIKE', '%'.$search.'%');
            $query->orWhere('ads.description', 'LIKE', '%'.$search.'%');
        }
        
        return $query->paginate(10);
    }

    // Category
    public function getCategories()
    {
        return Category::all();
    }
}