<?php

namespace App\Repositories;

use App\Note;
use Illuminate\Support\Facades\DB;
use Illuminate\Database\Eloquent\Model;

class NoteRepository implements RepositoryInterface
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
        return $this->model->paginate(10);
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
    public function search(array $data)
    {
        return $this->model->where('clubs.name', 'LIKE', '%'.$data['search'].'%')
              ->paginate(10);
    }

    public function getNotesByAdId($aid = '') {
        return $this->model
            ->where('ads_id', '=', $aid)
            ->where('user_id', '=', auth()->user()->id)
            ->get();
    }
}