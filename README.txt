Introduction
============
This README describes the data files on the novel of Pride and Prejudice by Jane Austen for the speaker identification task.

If you do use the data (or the ideas in our paper) I'd be interested in hearing about it. If the data go into academic research, a good scientific practice would probably recommend citing our paper in below, but of course ultimately that decision is yours based on how much information you use from our paper/data: 

Hua He, Denilson Barbosa, Grzegorz Kondrak.
Identification of Speakers in Novels.
In Proceedings of the 51st Annual Meeting of the Association for Computational Linguistics (ACL 2013), Sofia, Bulgaria.
Association for Computational Linguistics.


Data Description
============
1. File: PeopleList_Revised.txt
This is the provided people list in PP, 52 characters together with their gender and all aliases. Separated with semicolon.
Format: 
Name;Gender;Alias1;Alis2;Alias3;...

2. File: PRIDPREJ_NONEWLINE_Organize_v2.txt
This is the raw texts for the whole PP book. Utterance quotations start with ``, ends with ''.
Format: 
``But you forget, mama,'' said Elizabeth, ``that we shall meet him at the assemblies, and that Mrs. Long has promised to introduce him.''

3. File: REAL_ALL_CONTENTS_PP.txt
This is the annotation results on the whole PP novel, for all utterances in PP, 1294 sentences, separated by tabs.
Note that not all utterances are used in our paper, among 1294 utterances there are a couple of <LETTER> utterances and 'unsure' (by annotators) utterances that we think are essentially not proper for this speaker identification task, thus they are not included in the task. For example of <LETTER> utterances: In Ch21, "I do not pretend to regret any thing I shall leave in Hertfordshire, except your society, my dearest friend; but we ...", or in Chapter 26, "My dearest Lizzy will, I am sure, be incapable of triumphing in her better judgment, at my expence, ... Your's." However, a very majority part of total utterances are used.
Format: ChapterID \t Character \t Utterance


LICENSE
=============
Unless otherwise noted, you may assume that any data, included in this package are available under the license (see the LICENSE file).